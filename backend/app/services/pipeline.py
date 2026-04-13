import time
from datetime import datetime
from backend.app.services.parser import parse_file
from backend.app.services.section_splitter import split_sections
from backend.app.services.humanizer import humanize
from backend.app.services.paraphraser import paraphrase
from backend.app.services.grammar import improve_grammar
from backend.app.services.reconstruction import reconstruct
from backend.app.services.plagiarism import estimate_similarity
from backend.app.db.mongo import get_db
from backend.app.core.settings import settings
import os
from fastapi.concurrency import run_in_threadpool

async def log_step(db, job_id: str, step: str, message: str):
    await db.logs.insert_one({
        "job_id": job_id,
        "step": step,
        "message": message,
        "created_at": datetime.utcnow()
    })

async def run_pipeline(job_id: str, file_path: str, user_id: str):
    db = get_db()
    start = time.time()

    async def update_status(status: str, **kwargs):
        await db.jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow(), **kwargs}}
        )

    try:
        await update_status("parsing")
        await log_step(db, job_id, "parse", "Extracting text from document")
        raw_text = await run_in_threadpool(parse_file, file_path)
        word_count = len(raw_text.split())

        await update_status("splitting")
        await log_step(db, job_id, "split", f"Splitting into sections ({word_count} words)")
        sections = await run_in_threadpool(split_sections, raw_text)

        refined_sections = []
        for i, section in enumerate(sections):
            await log_step(db, job_id, "humanize", f"Humanizing section: {section['title']}")
            humanized = await humanize(section["content"])

            await log_step(db, job_id, "paraphrase", f"Paraphrasing section: {section['title']}")
            paraphrased = await paraphrase(humanized)

            await log_step(db, job_id, "grammar", f"Grammar check: {section['title']}")
            final = await improve_grammar(paraphrased)

            refined_sections.append({"title": section["title"], "refined": final})
            await update_status("processing", progress=round((i + 1) / len(sections) * 100))

        output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}.docx")
        await log_step(db, job_id, "reconstruct", "Reconstructing final document")
        await run_in_threadpool(reconstruct, refined_sections, output_path)

        refined_text = " ".join(s["refined"] for s in refined_sections)
        similarity = await run_in_threadpool(estimate_similarity, raw_text, refined_text)
        elapsed = round(time.time() - start, 2)

        await update_status(
            "completed",
            output_path=output_path,
            word_count=word_count,
            processing_time=elapsed,
            similarity_score=similarity
        )
        await log_step(db, job_id, "done", f"Completed in {elapsed}s. Similarity: {similarity}")

    except Exception as e:
        await update_status("failed", error=str(e))
        await log_step(db, job_id, "error", str(e))

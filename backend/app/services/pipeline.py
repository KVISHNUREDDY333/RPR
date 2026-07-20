import time
import os
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from backend.app.services.parser import parse_file
from backend.app.services.section_splitter import split_sections
from backend.app.services.reviewer import review_section
from backend.app.services.scorer import score_section
from backend.app.services.humanizer import humanize
from backend.app.services.reconstruction import reconstruct
from backend.app.services.report_generator import generate_review_report
from backend.app.services.feedback_generator import generate_overall_feedback
from backend.app.db.mongo import get_db
from backend.app.core.settings import settings


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
        # 1. Parse
        await update_status("parsing")
        await log_step(db, job_id, "parse", "Extracting text from document...")
        raw_text = await run_in_threadpool(parse_file, file_path)
        word_count = len(raw_text.split())

        if not raw_text.strip():
            raise ValueError("Document appears to be empty or unreadable.")

        # 2. Split
        await update_status("splitting")
        await log_step(db, job_id, "split", f"Splitting into sections ({word_count} words detected)...")
        sections = await run_in_threadpool(split_sections, raw_text)
        await log_step(db, job_id, "split", f"Found {len(sections)} section(s) to process.")

        section_analysis = []
        refined_sections = []
        total_score = 0.0

        # 3. Process each section
        for i, section in enumerate(sections):
            title = section["title"]
            progress = round((i / len(sections)) * 90)
            await update_status("processing", progress=progress)

            # Review
            await log_step(db, job_id, "review", f"Reviewing: {title}")
            review_data = await review_section(section["content"])

            # Score
            await log_step(db, job_id, "score", f"Scoring: {title}")
            score_data = await score_section(section["content"])

            section_analysis.append({
                "title": title,
                "score": score_data["score"],
                "reason": score_data["reason"],
                "clarity": review_data["clarity_rating"],
                "issues": review_data["issues"],
                "suggestions": review_data["suggestions"]
            })
            total_score += score_data["score"]

            # Refine
            await log_step(db, job_id, "refine", f"Refining: {title}")
            refined_content = await humanize(section["content"])
            refined_sections.append({"title": title, "refined": refined_content})

        # 4. Overall feedback
        await update_status("finalizing", progress=92)
        await log_step(db, job_id, "feedback", "Generating overall feedback...")
        analysis_summary = "\n".join(
            [f"{s['title']} (Score: {s['score']}): {s['reason']}" for s in section_analysis]
        )
        feedback = await generate_overall_feedback(analysis_summary)

        # 5. Reconstruct refined document
        await log_step(db, job_id, "reconstruct", "Building refined document...")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        refined_path = os.path.join(settings.OUTPUT_DIR, f"refined_{job_id}.docx")
        await run_in_threadpool(reconstruct, refined_sections, refined_path)

        # 6. Generate review report
        await log_step(db, job_id, "report", "Generating review report...")
        report_path = os.path.join(settings.OUTPUT_DIR, f"report_{job_id}.docx")
        overall_score = round(total_score / len(sections), 1) if sections else 0.0
        report_data = {
            **feedback,
            "section_analysis": section_analysis,
            "overall_score": overall_score
        }
        await run_in_threadpool(generate_review_report, report_data, report_path)

        # 7. Complete
        elapsed = round(time.time() - start, 2)
        await update_status(
            "completed",
            progress=100,
            output_path=refined_path,
            report_path=report_path,
            word_count=word_count,
            overall_score=overall_score,
            analysis=section_analysis,
            feedback=feedback,
            processing_time=elapsed
        )
        await log_step(db, job_id, "done", f"Completed in {elapsed}s. Score: {overall_score}/10")

    except Exception as e:
        import traceback
        err_msg = str(e)
        print(f"[Pipeline Error] {err_msg}")
        print(traceback.format_exc())
        await update_status("failed", error=err_msg)
        await log_step(db, job_id, "error", err_msg)

import time
import os
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from backend.app.services.parser import parse_file
from backend.app.services.section_splitter import split_sections
from backend.app.services.reviewer import review_section
from backend.app.services.scorer import score_section
from backend.app.services.humanizer import humanize # We can still use these or consolidate
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
        await log_step(db, job_id, "parse", "Extracting text from document")
        raw_text = await run_in_threadpool(parse_file, file_path)
        
        # 2. Split
        await update_status("splitting")
        await log_step(db, job_id, "split", "Analyzing structure and splitting sections")
        sections = await run_in_threadpool(split_sections, raw_text)

        section_analysis = []
        refined_sections = []
        total_score = 0

        # 3. Process each section (Review, Score, Refine)
        for i, section in enumerate(sections):
            section_title = section["title"]
            await update_status("processing", progress=round((i / len(sections)) * 100))
            await log_step(db, job_id, "review", f"Reviewing & Scoring: {section_title}")
            
            # AI Review & Score
            review_data = await review_section(section["content"])
            score_data = await score_section(section["content"])
            
            section_analysis.append({
                "title": section_title,
                "score": score_data["score"],
                "reason": score_data["reason"],
                "clarity": review_data["clarity_rating"],
                "issues": review_data["issues"]
            })
            total_score += score_data["score"]

            # AI Refinement (Humanization + Grammar)
            await log_step(db, job_id, "refine", f"Refining content: {section_title}")
            refined_content = await humanize(section["content"]) 
            refined_sections.append({"title": section_title, "refined": refined_content})

        # 4. Global Feedback
        await update_status("finalizing")
        await log_step(db, job_id, "feedback", "Generating overall feedback & report")
        
        analysis_summary = "\n".join([f"{s['title']} (Score: {s['score']}): {s['reason']}" for s in section_analysis])
        feedback = await generate_overall_feedback(analysis_summary)
        
        # 5. Document Reconstruction (Refined Paper)
        refined_output_path = os.path.join(settings.OUTPUT_DIR, f"refined_{job_id}.docx")
        await run_in_threadpool(reconstruct, refined_sections, refined_output_path)

        # 6. Report Generation
        report_path = os.path.join(settings.OUTPUT_DIR, f"report_{job_id}.docx")
        report_data = {
            **feedback,
            "section_analysis": section_analysis,
            "overall_score": round(total_score / len(sections), 1) if sections else 0
        }
        await run_in_threadpool(generate_review_report, report_data, report_path)

        # 7. Complete Job
        elapsed = round(time.time() - start, 2)
        await update_status(
            "completed",
            progress=100,
            output_path=refined_output_path,
            report_path=report_path,
            overall_score=report_data["overall_score"],
            analysis=section_analysis,
            feedback=feedback,
            processing_time=elapsed
        )
        await log_step(db, job_id, "done", f"Analysis complete in {elapsed}s")

    except Exception as e:
        await update_status("failed", error=str(e))
        await log_step(db, job_id, "error", str(e))
        print(f"[Pipeline Error] {str(e)}")

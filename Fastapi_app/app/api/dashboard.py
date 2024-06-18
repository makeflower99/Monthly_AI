from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from DB_app import models
from DB_app.models import Grading
from DB_app.dependencies import get_db
from app.QNA import summarize_article
import logging
from pathlib import Path

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/data", response_class=JSONResponse)
async def get_dashboard_data(article_code: str = Query(...), db: Session = Depends(get_db)):
    logger.info("Fetching data for article_code: %s", article_code)
    try:
        user_level = 2

        grading_data = db.query(
            Grading.is_correct
        ).filter(
            Grading.article_code == article_code
        ).all()

        result_text = summarize_article(article_code, db)

        total_count = len(grading_data)
        group_size = total_count // 3
        groups = []

        for i in range(3):
            start_index = i * group_size
            if i == 2:
                groups.append(grading_data[start_index:])
            else:
                groups.append(grading_data[start_index:start_index + group_size])

        scores = [sum(1 for item in group if item.is_correct == 1) for group in groups]

        article = db.query(models.Article).filter(models.Article.article_code == article_code).first()
        if not article:
            logger.error(f"Article not found for article_code: {article_code}")
            raise HTTPException(status_code=404, detail="Article not found")
        
        data = {
            "user_level": user_level,
            "scores": scores,
            "summary_text": result_text,
            "article_code": article_code,
            "article_content": article.content
        }
        
        results_entry = models.results(
            user_id=1,
            article_code=article_code,
            keyword_score=scores[0],
            vocabulary_score=scores[1],
            paragraph_score=scores[2],
            total_score=sum(scores)
        )
        
        db.add(results_entry)
        db.commit()
        return data
    except Exception as e:
        logger.error("Error fetching dashboard data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explanation", response_class=HTMLResponse)
async def explanation():
    html_content = Path("templates/explanation.html").read_text(encoding='utf-8')
    return HTMLResponse(content=html_content)

@router.get("/relecture", response_class=HTMLResponse)
async def relecture():
    html_content = Path("templates/ReLecture.html").read_text(encoding='utf-8')
    return HTMLResponse(content=html_content)

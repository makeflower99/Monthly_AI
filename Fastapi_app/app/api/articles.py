from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DB_app import models, schema
from DB_app.dependencies import get_db
from app.QNA import generate_all, generate_short_article, generate_middle_article, generate_long_article, initialize_generation
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/generate_article", response_model=schema.NewsResponse)
def create_news(db: Session = Depends(get_db)):
    try:
        response_data = generate_all()
        return response_data
    except Exception as e:
        logger.error(f"Error generating article: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate article")
    
@router.post("/generate/short", response_model=schema.ArticleResponse)
def generate_short(db: Session = Depends(get_db)):
    client, sub = initialize_generation()
    try:
        result = generate_short_article(client, db, sub)
        if isinstance(result, dict):
            return schema.ArticleResponse(
                article_code=result.get("article_code", "default_article_code"),
                difficulty="short",
                title=result.get("title", "default_title"),
                date=result.get("date", "default_date"),
                author=result.get("author", "default_author"),
                paragraph1=result.get("paragraph1", "default_paragraph1"),
                paragraph2=result.get("paragraph2", "default_paragraph2"),
                paragraph3=result.get("paragraph3", "default_paragraph3"),
                paragraph4=result.get("paragraph4", "default_paragraph4"),
                questions=result.get("questions", [])
            )
        else:
            raise ValueError("Unexpected result format from generate_short_article")
    except Exception as e:
        logger.error(f"Error generating short article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate short article: {e}")

@router.post("/generate/middle", response_model=schema.ArticleResponse)
def generate_middle(db: Session = Depends(get_db)):
    client, sub = initialize_generation()
    try:
        result = generate_middle_article(client, db, sub)
        if isinstance(result, dict):
            return schema.ArticleResponse(
                article_code=result.get("article_code", "default_article_code"),
                difficulty="middle",
                title=result.get("title", "default_title"),
                date=result.get("date", "default_date"),
                author=result.get("author", "default_author"),
                paragraph1=result.get("paragraph1", "default_paragraph1"),
                paragraph2=result.get("paragraph2", "default_paragraph2"),
                paragraph3=result.get("paragraph3", "default_paragraph3"),
                paragraph4=result.get("paragraph4", "default_paragraph4"),
                questions=result.get("questions", [])
            )
        else:
            raise ValueError("Unexpected result format from generate_middle_article")
    except Exception as e:
        logger.error(f"Error generating middle article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate middle article: {e}")

@router.post("/generate/long", response_model=schema.ArticleResponse)
def generate_long(db: Session = Depends(get_db)):
    client, sub = initialize_generation()
    try:
        result = generate_long_article(client, db, sub)
        if isinstance(result, dict):
            return schema.ArticleResponse(
                article_code=result.get("article_code", "default_article_code"),
                difficulty="long",
                title=result.get("title", "default_title"),
                date=result.get("date", "default_date"),
                author=result.get("author", "default_author"),
                paragraph1=result.get("paragraph1", "default_paragraph1"),
                paragraph2=result.get("paragraph2", "default_paragraph2"),
                paragraph3=result.get("paragraph3", "default_paragraph3"),
                paragraph4=result.get("paragraph4", "default_paragraph4"),
                questions=result.get("questions", [])
            )
        else:
            raise ValueError("Unexpected result format from generate_long_article")
    except Exception as e:
        logger.error(f"Error generating long article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate long article: {e}")

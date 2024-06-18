from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from DB_app import models, crud, schema
from DB_app.dependencies import get_db
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/questions_by_article_code", response_class=JSONResponse)
async def get_question_codes_by_article_code(article_code: str = Query(...), db: Session = Depends(get_db)):
    questions = db.query(models.Question).filter(models.Question.article_code == article_code).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")

    question_codes = [question.question_code for question in questions]
    
    return {"question_codes": question_codes}

@router.get("/Difficulty/level1/data", response_class=JSONResponse)
async def get_difficulty_level1_data(difficulty: str = Query("short"), article_code: str = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching questions with difficulty: {difficulty} and article_code: {article_code}")
    
    if article_code is None:
        logger.error("Article code is None")
        raise HTTPException(status_code=400, detail="Article code must be provided")

    questions = db.query(models.Question).join(models.Article).filter(
        models.Article.difficulty == difficulty,
        models.Question.article_code == article_code
    ).all()
    
    if not questions:
        logger.error("Questions not found")
        raise HTTPException(status_code=404, detail="Questions not found")
    
    logger.info(f"Questions found: {len(questions)}")
    
    article = db.query(models.Article).filter(models.Article.article_code == article_code).first()
    if not article:
        logger.error(f"Article not found for article_code: {article_code}")
        raise HTTPException(status_code=404, detail="Article not found")
    
    logger.info(f"Article found: {article.title}")

    questions_list = []
    for question in questions:
        questions_list.append({
            "question": question.question,
            "options": [
                question.option1,
                question.option2,
                question.option3,
                question.option4
            ],
            "answer": question.answer,
            "explanation": question.explanation
        })
    
    item_dict = {
        "questions": questions_list,
        "articles": [
            {
                "title": article.title,
                "date": article.date,
                "author": article.author,
                "paragraph1": article.paragraph1,
                "paragraph2": article.paragraph2,
                "paragraph3": article.paragraph3,
                "paragraph4": article.paragraph4,
                "content": article.content
            }
        ],
        "total": len(questions_list)
    }
    logger.info("Returning response")
    return item_dict

@router.get("/Difficulty/realtime/data", response_class=JSONResponse)
async def get_difficulty_realtime_data(difficulty: str = Query("short"), article_code: str = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching questions with difficulty: {difficulty} and article_code: {article_code}")
    
    if article_code is None:
        logger.error("Article code is None")
        raise HTTPException(status_code=400, detail="Article code must be provided")

    questions = db.query(models.Question).join(models.Article).filter(
        models.Article.difficulty == difficulty,
        models.Question.article_code == article_code
    ).all()
    
    if not questions:
        logger.error("Questions not found")
        raise HTTPException(status_code=404, detail="Questions not found")
    
    logger.info(f"Questions found: {len(questions)}")
    
    article = db.query(models.Article).filter(models.Article.article_code == article_code).first()
    if not article:
        logger.error(f"Article not found for article_code: {article_code}")
        raise HTTPException(status_code=404, detail="Article not found")
    
    logger.info(f"Article found: {article.title}")

    questions_list = []
    for question in questions:
        questions_list.append({
            "question": question.question,
            "options": [
                question.option1,
                question.option2,
                question.option3,
                question.option4
            ],
            "answer": question.answer,
            "explanation": question.explanation
        })
    
    item_dict = {
        "questions": questions_list,
        "articles": [
            {
                "title": article.title,
                "date": article.date,
                "author": article.author,
                "paragraph1": article.paragraph1,
                "paragraph2": article.paragraph2,
                "paragraph3": article.paragraph3,
                "paragraph4": article.paragraph4,
                "content": article.content
            }
        ],
        "total": len(questions_list)
    }
    logger.info("Returning response")
    return item_dict

@router.get("/Difficulty/level1/{item_id}", response_model=schema.News)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/Difficulty/level1", response_model=schema.News)
async def create_item(item: schema.NewsCreate, db: Session = Depends(get_db)):
    db_item = crud.create_item(db, item)
    return db_item

@router.post("/submit_answers")
async def submit_answers(submissions: models.MultipleAnswerSubmission, db: Session = Depends(get_db)):
    logger.info("Received submissions: %s", submissions)  # 수정된 부분
    for submission in submissions.answers:
        logger.info("Processing submission: %s", submission)
        question = db.query(models.Question).filter(
            models.Question.article_code == submission.article_code,
            models.Question.question_code == submission.question_code
        ).first()

        if not question:
            logger.error(f"Question not found for article_code: {submission.article_code}, question_code: {submission.question_code}")
            raise HTTPException(status_code=404, detail=f"Question {submission.question_code} not found")

        is_correct = 1 if submission.submitted_answer == question.answer else 0

        existing_entry = db.query(models.Grading).filter(
            models.Grading.user_id == submission.user_id,
            models.Grading.article_code == submission.article_code,
            models.Grading.question_code == submission.question_code
        ).first()

        if existing_entry:
            existing_entry.submitted_answer = submission.submitted_answer
            existing_entry.is_correct = is_correct
        else:
            grading_entry = models.Grading(
                user_id=submission.user_id,
                article_code=submission.article_code,
                question_code=submission.question_code,
                submitted_answer=submission.submitted_answer,
                is_correct=is_correct
            )
            db.add(grading_entry)
    db.commit()
    return {"detail": "All answers submitted successfully"}

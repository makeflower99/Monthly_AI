from sqlalchemy.orm import Session
from DB_app.models import Article, News, Question, Grading, results
from DB_app.schema import NewsCreate
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_items(db: Session):
    return db.query(News).all()

def get_item(db: Session, item_id: int):
    return db.query(News).filter(News.id == item_id).first()

def create_item(db: Session, item: NewsCreate):
    db_item = News(article=item.article)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    questions_list = []
    for question in item.questions:
        db_question = Question(
            question=question.question,
            answer=question.answer,
            option1=question.options[0],
            option2=question.options[1],
            option3=question.options[2],
            option4=question.options[3],
            news_id=db_item.id
        )
        db.add(db_question)
        questions_list.append(db_question)
    db.commit()
    
    db_item.questions = questions_list
    return db_item

def update_item(db: Session, db_item: News, updated_item: NewsCreate):
    db_item.article = updated_item.article
    db.commit()
    db.refresh(db_item)
    
    for question in updated_item.questions:
        db_question = db.query(Question).filter(Question.news_id == db_item.id, Question.question == question.question).first()
        if db_question:
            db_question.answer = question.answer
            db_question.option1 = question.options[0]
            db_question.option2 = question.options[1]
            db_question.option3 = question.options[2]
            db_question.option4 = question.options[3]
        else:
            db_question = Question(
                question=question.question,
                answer=question.answer,
                option1=question.options[0],
                option2=question.options[1],
                option3=question.options[2],
                option4=question.options[3],
                news_id=db_item.id
            )
            db.add(db_question)
    db.commit()
    return db_item

def delete_item(db: Session, db_item: News):
    db.delete(db_item)
    db.commit()

def get_question(db: Session, question_code: int):
    return db.query(Question).filter(Question.question_code == question_code).first()

def get_questions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Question).offset(skip).limit(limit).all()

def get_article_by_code(db: Session, article_code: str):
    return db.query(Article).filter(Article.article_code == article_code).first()

def get_next_article_code(db: Session) -> str:
    last_article = db.query(Article).order_by(Article.article_code.desc()).first()
    if last_article and last_article.article_code and isinstance(last_article.article_code, str):
        try:
            last_code = int(last_article.article_code.split('-')[1])
            new_code = f"{last_code + 1:03d}"
        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing article code: {e}")
            new_code = "001"
    else:
        new_code = "001"
    return f"ART-{new_code}"

def save_generated_data(db: Session, level: str, article_data: dict, keyword_data: dict, voca_data: dict, article_questions_data: dict, summary_data:dict, sub: str):
    today_date = datetime.today().strftime('%Y-%m-%d')

    # 기존의 article_code를 덮어쓰지 않도록 수정
    article_code_base = article_data.get('article_code', '001')
    if article_code_base.startswith("ART-"):
        article_code_base = article_code_base.split('-')[1]
    article_code = f"ART-{article_code_base}-{level}"

    article = Article(
        article_code=article_code,
        title=article_data.get("Title", "No Title"),
        date=today_date,
        author=article_data.get("Author", "듬이 기자"),
        content=sub,
        paragraph1=article_data.get("paragraph 1", ""),
        paragraph2=article_data.get("paragraph 2", ""),
        paragraph3=article_data.get("paragraph 3", ""),
        paragraph4=article_data.get("paragraph 4", ""),
        difficulty=level
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    news = News(article=article.content)
    db.add(news)
    db.commit()
    db.refresh(news)

    response_data = {
        "id": news.id,
        "article_code": article_code,
        "article": news.article,
        "questions": []
    }

    print("Starting to save keyword questions")
    save_questions(db, keyword_data, article_code, news.id, response_data, "keyword")
    print("Finished saving keyword questions")

    print("Starting to save voca questions")
    save_questions(db, voca_data, article_code, news.id, response_data, "voca")
    print("Finished saving voca questions")

    print("Starting to save article questions")
    save_questions(db, article_questions_data, article_code, news.id, response_data, "organize")
    print("Finished saving article questions")

    print("Starting to save summary")
    save_summary(db, summary_data, article_code, news.id, response_data)
    print("Finished saving summary")

    return response_data



def save_questions(db, question_data, article_code, news_id, response_data, question_type):
    question_keys = [key for key in question_data.keys() if key.startswith(f"{question_type}_question_")]
    for key in question_keys:
        index = key.split('_')[-1]
        answer_key = f"{question_type}_answer_{index}"
        options_key = f"{question_type}_option_{index}"
        options = question_data.get(options_key, [])

        # None 값 처리
        options = [opt if opt is not None else "" for opt in options]

        print(f"Processing question: {key}, answer: {answer_key}, options: {options}")  # 디버그 로그 추가

        db_question = Question(
            question=question_data[key],
            answer=question_data[answer_key],
            option1=options[0] if len(options) > 0 else "",
            option2=options[1] if len(options) > 1 else "",
            option3=options[2] if len(options) > 2 else "",
            option4=options[3] if len(options) > 3 else "",
            article_code=article_code,
            news_id=news_id,
        )

        print(f"Saving question: {db_question.question}, options: {options}")  # 디버그 로그 추가

        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        response_data["questions"].append({
            "question_code": db_question.question_code,
            "news_id": db_question.news_id,
            "question": db_question.question,
            "answer": db_question.answer,
            "options": [db_question.option1, db_question.option2, db_question.option3, db_question.option4],
        })

def save_summary(db, question_data, article_code, news_id, response_data):
    db_question = Question(
        question="기사내용을 바탕으로 나만의 요약문을 작성해보세요.",
        answer=question_data['summary'],
        option1="A",
        option2="B",
        option3="C",
        option4="D",
        article_code=article_code,
        news_id=news_id,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    response_data["questions"].append({
        "question_code": db_question.question_code,
        "news_id": db_question.news_id,
        "question": db_question.question,
        "answer": db_question.answer,
        "options": [db_question.option1, db_question.option2, db_question.option3, db_question.option4],
    })

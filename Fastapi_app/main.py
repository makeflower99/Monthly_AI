from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import articles, dashboard, questions
from sqlalchemy.orm import Session
from DB_app import models, DBsetting
from DB_app.DBsetting import SessionLocal
import logging
import os
import csv
from contextlib import asynccontextmanager

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_all_tables():
    models.Base.metadata.create_all(bind=DBsetting.engine)

# CSV 파일에서 데이터를 읽어 DB에 삽입하는 함수
def load_csv_to_db(db: Session, file_path: str, model, foreign_key_check=False):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if foreign_key_check and 'news_id' in row:
                news_id = row['news_id']
                if not db.query(models.News).filter(models.News.id == news_id).first():
                    logger.warning(f"Skipping row with invalid news_id: {news_id}")
                    continue
            db.add(model(**row))
    db.commit()

def initialize_db_with_csv_data(db: Session):
    flask_app_data_path = "/app/data"
    articles_path = os.path.join(flask_app_data_path, "articles.csv")
    questions_path = os.path.join(flask_app_data_path, "questions.csv")
    news_path = os.path.join(flask_app_data_path, "news.csv")

    # 먼저 news 데이터를 로드
    if os.path.exists(news_path):
        load_csv_to_db(db, news_path, models.News)
    
    # 그 다음 articles 데이터를 로드
    if os.path.exists(articles_path):
        load_csv_to_db(db, articles_path, models.Article)

    # 마지막으로 questions 데이터를 로드 (foreign_key_check를 True로 설정)
    if os.path.exists(questions_path):
        load_csv_to_db(db, questions_path, models.Question, foreign_key_check=True)

# 앱이 시작될 때 DB를 초기화하고 샘플 데이터를 추가하는 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    try:
        create_all_tables()
        logger.info("Database initialized successfully")
        db = SessionLocal()
        try:
            initialize_db_with_csv_data(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    yield
    logger.info("Shutting down...")

app.router.lifespan_context = lifespan

app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

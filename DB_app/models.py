from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Sequence
from sqlalchemy.orm import relationship
from DB_app.DBsetting import Base
from pydantic import BaseModel

class News(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article = Column(String(2000))

    questions = relationship("Question", back_populates="news")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_code = Column(String(50), unique=True, index=True)  
    title = Column(String(255)) 
    date = Column(Date)
    author = Column(String(255)) 
    content = Column(String(2000)) 
    paragraph1 = Column(String(2000)) 
    paragraph2 = Column(String(2000)) 
    paragraph3 = Column(String(2000)) 
    paragraph4 = Column(String(2000)) 
    difficulty = Column(String(10), default='unknown')  # 난이도 컬럼 추가

    questions = relationship("Question", back_populates="article")

class Question(Base):
    __tablename__ = "questions"

    question_code = Column(Integer, Sequence('question_code_seq'), primary_key=True, autoincrement=True)
    article_code = Column(String(50), ForeignKey("articles.article_code"))  
    question = Column(String(2000)) 
    option1 = Column(String(2000),nullable=True) 
    option2 = Column(String(2000),nullable=True) 
    option3 = Column(String(2000),nullable=True) 
    option4 = Column(String(2000),nullable=True) 
    answer = Column(String(2000)) 
    explanation = Column(String(2000)) 
    news_id = Column(Integer, ForeignKey("items.id"))

    article = relationship("Article", back_populates="questions")
    news = relationship("News", back_populates="questions")

class Grading(Base):
    __tablename__ = "grading"
    
    user_id = Column(Integer, primary_key=True)
    article_code = Column(String(50), primary_key=True)  
    question_code = Column(Integer, primary_key=True)
    submitted_answer = Column(String(2000)) 
    is_correct = Column(Boolean)

class results(Base):
    __tablename__ = "results"
    
    idx = Column(Integer, primary_key=True, autoincrement=True)
    article_code = Column(String(50), ForeignKey("articles.article_code"))
    user_id = Column(Integer)
    keyword_score = Column(Integer)
    vocabulary_score = Column(Integer)
    paragraph_score = Column(Integer) 
    total_score = Column(Integer)

class AnswerSubmission(BaseModel):
    user_id: int
    article_code: str
    question_code: int
    submitted_answer: str

class MultipleAnswerSubmission(BaseModel):
    answers: list[AnswerSubmission]

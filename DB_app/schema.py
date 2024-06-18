from typing import List
from pydantic import BaseModel

class QuestionBase(BaseModel):
    question: str
    answer: str
    options: List[str]

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    question_code: int
    news_id: int

    class Config:
        orm_mode = True

class NewsBase(BaseModel):
    article: str

class NewsCreate(NewsBase):
    questions: List[QuestionCreate] = []

class News(NewsBase):
    id: int
    questions: List[Question]

    class Config:
        orm_mode = True

class NewsResponse(BaseModel):
    articles: List[News]

# New schema for short, middle, long articles
class ArticleBase(BaseModel):
    title: str
    date: str
    author: str
    paragraph1: str
    paragraph2: str
    paragraph3: str
    paragraph4: str
    difficulty: str

class ArticleResponse(ArticleBase):
    article_code: str
    questions: List[Question]

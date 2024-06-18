from DB_app.DBsetting import engine, Base
from DB_app.models import *

# 테이블 생성 함수
def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")

if __name__ == "__main__":
    create_all_tables()

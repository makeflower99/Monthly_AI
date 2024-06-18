# 베이스 이미지 설정
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# netcat 설치 및 시간대 설정
RUN apt-get update && apt-get install -y netcat-openbsd tzdata

# 시간대를 로컬 시간대로 설정 (예: Asia/Seoul)
ENV TZ=Asia/Seoul

# 필요 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# wait-for-it.sh 스크립트 복사 및 실행 권한 부여
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# 애플리케이션 소스 복사
COPY . .

# FastAPI 실행 명령 설정
CMD ["/bin/sh", "-c", "/wait-for-it.sh mysql:3306 --timeout=600 --strict -- uvicorn main:app --host 0.0.0.0 --port 8000 & python /app/generate_article_job.py"]

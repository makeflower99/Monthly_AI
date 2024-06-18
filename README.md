![AI 월간 밀크T cover](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/d141b524-7484-43c0-8681-c9eef732cbb5)

![버전](https://img.shields.io/badge/version-1.0.0-blue)

# 📌AI 월간 밀크T
생성형 AI를 통해 매월 신문기사와 문해력 관련 문제를 제공 하는 서비스 입니다.
코드를 수정하여 주제를 바꾸거나 프롬프트를 수정하여 원하는 수준의 혹은 유형의 문제로 바꿔서 사용 할 수 있습니다.

## 📌프로젝트 요약
최근 매체에선 성인 문해력 뿐만 아니라 청소년들의 문해력 하락에 대한 우려섞인 의견이 많이 등장하고 있다. 따라서 중학교 학생들을 대상으로, 신문기사를 읽는 경험을 늘리고 관련된 문제를 풀어보면서 스스로 긴 글에서 정보를 탐색, 글의 요지를 파악하여 문해력을 향상시키는 연습을 하는것을 이번 프로젝트의 목표로 설정했다.

이번 프로젝트는 GPT-4o 모델을 활용하여 기사와 문해력 관련 문제를 자동으로 생성하도록 시스템을 구축하였다. 이는 문해력 관련 자료를 인력의 도움 없이 제작할 수 있기에 인건비 절감 효과가 있다.

이번 프로젝트는 밀크티 서비스를 사용하는 중학생의 사이트 체류시간의 증가, 중학생들의 문해력 수준을 파악할 수 있는 데이터의 수집, 강좌 추천을 통한 강의 컨텐츠 홍보를 기대할 수 있다.

## 📌기능
- 원하는 분량의 신문기사와 문제 선택
- 객관식 뿐만 아니라 직접 작성한 요약문에 대한 피드백
- 실시간으로 gpt api에 연결하여 추가적인 기사와 문제 생성가능
- 어떤 문제를 틀렸는지와 정답 확인
- 핵심어 문제의 경우에는 키워드를 추출 할 수있는 방법과 결과 형식를 함께 프롬프트를 보내 각 문단과 각 문장의 핵심어를 추출할 수 있다. 이후에는 파이썬 코드를 통해 구체적인 문제형식을 제작했다.
- 어휘 문제의 경우 문제와 정답, 보기를 전부 생성형AI에게 만들도록 하였다. 현재의 어휘문제는 반의어, 동의어 단어의 정의 등을 질문하는 형태로 이루어져 있다.
- 내용파악 문제의 경우 정해진 문제형식이 없기 때문에 PISA에서 문해력 측정에 사용하는 문제의 예시와 정답 및 보기를 인공지능에서 함께 제공하여, 본문내용에 기반한 문제로 만들 수 있도록 구현하였다.

| 유형 | 기사 | 핵심어 | 어휘 | 내용파악 |
|--------|------|------|------|------|
| 짧은글 | 2문단 | 3문제 | 3문제 | 3문제 |
| 중간글 | 3문단 | 4문제 | 4문제 | 4문제 |
| 긴 글 | 4문단 | 5문제 | 5문제 | 5문제 |

## 📌설치 및 실행 방법
**docker를 설치 완료 한 후 실행 해주세요.**
**파일은 clone하지 말고 압축폴더 다운로드해서 실행해주세요.**
**가상환경을 필수가 아니지만 권장합니다.**
>루트 폴더에 .env 생성
```bash
# .env 내용
# API key
GPT_API_KEY="your-api-key"

# Database configuration
DB_HOST="your-db-host"
DB_PORT="your-db-port"
DB_USER="your-db-user"
DB_PASSWORD="your-db-password"
DB_NAME="your-db-name"
```
> 만약 3306 포트를 다른 데이터 베이스가 사용하고 있는 경우 : docker-compose 파일에서 sql 포트번호를 바꿔서 진행하세요
```bash
# 예시
    ports:
      - "3307:3306"
```
>가상환경 생성
```bash
python -m venv 가상환경이름
```
>가상환경 실행 : 가상환경이름/Scripts/ 경로에서 cmd 창에 아래코드 실행
```bash
activate.bat
```
>가상환경 실행 후 .env가 있는 폴더로 이동 후 cmd 혹은 powershell 창에 아래 코드 입력
```bash
docker-compose up --build
```
>생성된 로컬주소로 이동해 주세요🚀
```bash
127.0.0.1:5000
```
## 📌실제 서비스 화면
< 메인페이지 >
![Screenshot 2024-06-17 205300](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/ef7d7b92-0377-45cb-8fc0-d4d0d54b97b6)

< 난이도 선택 페이지 >
![Screenshot 2024-06-17 205305](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/f6380eb0-b6bb-425c-aa67-4ea4c130a1ac)

< 문제페이지 >
![Screenshot 2024-06-17 205322](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/1c718b2c-b050-4145-adc8-89bafeed6858)

< 대시보드 >
![Screenshot 2024-06-17 205641](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/fde17f86-34c0-4cb7-b219-b5232328f231)

< 정답지 페이지 >
![Screenshot 2024-06-17 205657](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/a670f747-67c6-4360-9966-fa5c3a7454e5)

< 추천강좌 페이지 >
![Screenshot 2024-06-17 205702](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/57c0582b-dad2-4109-87e4-cb33950b3bf9)

< 생각넓히기 페이지 >
![Screenshot 2024-06-17 205706](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/a1a41f03-4329-4055-9b91-a527b2c49036)


## 📌아키텍처
![아키텍처 (5)](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/71313259/73fe08b5-9913-4a79-a339-e32e6320fdcb)

## 📌ERD
![Screenshot 2024-06-05 145910](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/aaf384ea-a540-4ba4-bf7b-b44e3197d4aa)

## 📌라이브러리
![Screenshot 2024-06-14 112723](https://github.com/wonjin-hwang/chunjae_Monthly_MKT/assets/156271091/e91f61c8-1491-4af9-931b-48565b4c8d8b)

## 📌구성원
| 이름 | 역할 |
|--------|------|
| 송희도 | DB 구축, api 서버 구축, 웹제작 |
| 조서연 | 기획, 웹제작, 프롬프트 엔지니어링 |
| 황원진 | DB 구축, 프롬프트 엔지니어링, 웹제작 |

## 📌주의사항
현재 실험해본 결과 대략 30개의 테스트 중 어휘 문제에서 2개 가량의 문제가 발생한 것으로 보이고 이는 6.6666%의 오류가 있다는 것을 의미한다.
또한, 생성형 AI의 경우 프롬프트가 길수록 그리고 원하는 답변이 길수록 다양한 값이 등장할 위험 부담이 크다. 따라서 에러가 발생할 경우 에러가 발생한 원인과 위치를 출력하고 최대 3번 재실행 하도록 예외처리를 해두었다.

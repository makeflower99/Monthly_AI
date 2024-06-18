from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import pandas as pd
import os

app = Flask(__name__)

@app.context_processor
def utility_processor():
    def zip_lists(a, b):
        return zip(a, b)
    return dict(zip=zip_lists)

@app.route('/')
def home():
    return render_template('MainIndex.html', message="This is a dynamic message from the server!")

@app.route('/Difficulty')
def difficulty():
    return render_template('Difficulty.html')

@app.route('/Difficulty/level1')
def difficulty_level1():
    difficulty = request.args.get('difficulty')
    article_code = request.args.get('article_code')
    
    app.logger.info(f"Fetching data for difficulty: {difficulty}, article_code: {article_code}")
    
    if not difficulty or not article_code:
        difficulty = request.cookies.get('difficulty', 'short')
        article_code = request.cookies.get('article_code', 'ART-001-short')
        app.logger.info(f"Using default values - difficulty: {difficulty}, article_code: {article_code}")

    try:
        response = requests.get(f'http://fastapi_app:8000/api/questions/Difficulty/level1/data?difficulty={difficulty}&article_code={article_code}')
        response.raise_for_status()
        data = response.json()
        return render_template('level/level1.html', questions=data['questions'], articles=data['articles'])
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from FastAPI: {e}")
        return f"Error fetching data: {e}", 500

@app.route('/Difficulty/realtime')
def difficulty_realtime():
    difficulty = request.args.get('difficulty')
    article_code = request.args.get('article_code')
    
    app.logger.info(f"Fetching data for difficulty: {difficulty}, article_code: {article_code}")
    
    if not difficulty or not article_code:
        difficulty = request.cookies.get('difficulty', 'short')
        article_code = request.cookies.get('article_code', 'ART-001-short')
        app.logger.info(f"Using default values - difficulty: {difficulty}, article_code: {article_code}")

    try:
        response = requests.get(f'http://fastapi_app:8000/api/questions/Difficulty/realtime/data?difficulty={difficulty}&article_code={article_code}')
        response.raise_for_status()
        data = response.json()
        return render_template('level/realtime.html', questions=data['questions'], articles=data['articles'])
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from FastAPI: {e}")
        return f"Error fetching data: {e}", 500

@app.route('/dashboard')
def dashboard():
    article_code = request.args.get('article_code')
    if not article_code:
        article_code = request.cookies.get('article_code', 'ART-001-short')
    app.logger.info(f"Setting article_code in dashboard: {article_code}")
    ai_summary_local = request.cookies.get('question_39')
    app.logger.info(f"ai_summary: {ai_summary_local}")

    try:
        response = requests.get(f'http://fastapi_app:8000/api/dashboard/data?article_code={article_code}')
        response.raise_for_status()
        data = response.json()
        return render_template(
            'Dashboard.html', 
            user_level=data['user_level'], 
            scores=data['scores'], 
            summary_text=data['summary_text'], 
            article_code=article_code,
            article_content=data['article_content'],  # 추가된 부분
            ai_summary=data['summary_text']  # 추가된 부분
        )
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from FastAPI: {e}")
        return f"Error fetching data: {e}", 500


@app.route('/dashboard/explanation')
def explanation():
    difficulty = request.args.get('difficulty', 'short')
    article_code = request.args.get('article_code')
    app.logger.info(f"Fetching data for difficulty: {difficulty}, article_code: {article_code}")

    if not article_code:
        app.logger.error("Article code is missing")
        return "Article code is required", 400

    try:
        response = requests.get(f'http://fastapi_app:8000/api/questions/Difficulty/level1/data?difficulty={difficulty}&article_code={article_code}')
        response.raise_for_status()
        data = response.json()

        questions = data['questions']
        article_content = [q['answer'] for q in questions]  # 예시로 questions에서 answer를 추출

        return render_template('explanation.html', questions=questions, article_code=article_code, article_content=article_content)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from FastAPI: {e}")
        return f"Error fetching data: {e}", 500

@app.route('/dashboard/relecture')
def relecture():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'lecturelist.xlsx')
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    df.columns = df.iloc[1]
    df = df.drop([0, 1]).reset_index(drop=True)
    lecture_json = df.to_json(orient='records', force_ascii=False)
    
    app.logger.info(f'Lecture JSON: {lecture_json}')  # 로그에 JSON 데이터 출력
    
    return render_template('relecture.html', lecture_json=lecture_json)

@app.route('/gradio')
def gradio():
    return render_template('gradio.html')

@app.route('/get_data')
def get_data():
    response = requests.get('http://fastapi_app:8000/api_endpoint')
    data = response.json()
    return jsonify(data)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    print("submit_answers : Y")
    json_data = request.get_json()
    response = requests.post('http://fastapi_app:8000/api/questions/submit_answers', json=json_data)
    
    try:
        data = response.json()
        return jsonify(data)
    except ValueError as e:
        app.logger.error(f"Error decoding JSON response: {e}")
        return jsonify({"detail": "Error decoding JSON response"}), 500

@app.route('/Bulletinboard/Broadening')
def broadening():
    return render_template('Bulletinboard/Broadening.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

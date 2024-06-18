import schedule
import time
import requests

def generate_article():
    url = 'http://fastapi_app:8000/api/generate_article'
    response = requests.post(url, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        data = response.json()
        print("Article generated successfully:", data)
    else:
        print(f"Failed to generate article. Status code: {response.status_code}")

# 하루에 한 번 실행
schedule.every().day.at("15:35").do(generate_article)
# schedule.every(30).days.at("00:00").do(generate_article)

while True:
    schedule.run_pending()
    time.sleep(1)

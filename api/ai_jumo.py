import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv() # .env 파일에서 키를 불러옵니다.
api_key = os.environ.get('OPENAI_API_KEY') 

# 1. 임시 데이터
region = "제주도"
taste = "상큼한"

# 2. AI 주모에게 내릴 특별 지시사항 (프롬프트)
system_instruction = """
너는 한국의 전통주를 꿰뚫고 있는 친근한 주막의 주모야.
[엄격한 규칙]
1. 반드시 '실제로 존재하는' 막걸리만 추천할 것. 절대 가상의 이름을 지어내지 마.
2. 추천한 막걸리와 찰떡궁합인 안주를 한개 또는 두개 같이 추천해 줘.
3. 말투는 "~했소", "~어떠소?" 같은 친근하고 구수한 사극 톤을 사용해. 다만, 너무 과하지 않게 자연스럽게 해줘.
"""

# 3. 교육장 서버로 요청 보내기 세팅
url = "https://copa.codyssey.kr/v1/chat/completions"

# 🌟 학생님이 완벽하게 작성하신 환경변수 적용 부분!
headers = {
    "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-5-mini", 
    "messages": [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"{region} 지역의 {taste} 맛이 나는 막걸리 추천해 주시오!"}
    ]
}

# 4. AI에게 질문 던지고 결과 받기
print("AI 주모가 생각 중입니다... ⏳\n")
response = requests.post(url, headers=headers, json=data)

# 5. 결과 출력하기
if response.status_code == 200:
    result = response.json()
    print("🍶 [주모의 추천]")
    print(result["choices"][0]["message"]["content"])
else:
    print(f"앗! 에러가 발생했소: {response.status_code}")
    print(response.text)
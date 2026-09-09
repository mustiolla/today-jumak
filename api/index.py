from flask import Flask, request, jsonify
import requests
import os  # 👈 환경변수(API 키)를 불러오기 위해 필요합니다!

app = Flask(__name__)

# 2. AI에게 추천을 요청받고 결과를 돌려주는 길 안내
@app.route('/api/recommend', methods=['POST'])
def recommend():
    # 웹페이지에서 보낸 지역과 맛 데이터 받기
    data = request.json
    region = data.get('region')
    taste = data.get('taste')

    # AI 주모 프롬프트 (규칙 정리 완료!)
    system_instruction = """
    당신은 한국의 전통 주막을 운영하는 친근하고 호탕한 '주모'입니다.
    사용자가 원하는 지역(생산지 기준)과 맛을 알려주면, 다음 규칙을 무조건 지켜서 대답하세요.

    1. ⭐️ 절대 사용자에게 다시 질문하거나 되묻지 마세요. (예: "어떤 걸 원하소?" 금지)
    2. 조건에 맞는 막걸리 딱 1개와, 그에 어울리는 안주 1개 또는 2개를 즉시 확정해서 추천해 주세요.
    3. 만약 해당 지역에 딱 맞는 막걸리가 없다면, 가장 비슷하거나 유명한 막걸리로 주모가 알아서 골라주세요.
    4. 가능하다면, 서울에서 추천 막걸리를 구입할 수 있는지 여부도 함께 알려 주세요. 판매 여부가 확실하지 않다면 "현재, 서울에서 구입 가능하지 않소"라고 알려 주세요. 
    5. 말투는 반드시 "~했소", "~구려", "아이고 손님!" 같은 친근한 사극 주모 톤을 유지하세요. 다만, 너무 과하지 않게 자연스럽게 해주세요. 
    6. 답변을 할 때 추천하는 막걸리 이름과 안주 이름은 반드시 HTML <strong> 태그로 감싸서 강조해 주세요. (예시: <strong>느린마을 막걸리</strong>)
    """

    url = "https://copa.codyssey.kr/v1/chat/completions"
    
    # 🚨 수정됨: API 키를 코드에 직접 적지 않고, Vercel 환경변수에서 안전하게 가져옵니다!
    api_key = os.environ.get('OPENAI_API_KEY')
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {
        "model": "gpt-4o-mini",  # 🚨 수정됨: 존재하는 모델 이름으로 변경!
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"{region} 지역의 {taste} 맛이 나는 막걸리 추천해 주시오!"}
        ]
    }

    # AI에게 요청 보내기
    response = requests.post(url, headers=headers, json=payload)

    # 결과 돌려주기
    if response.status_code == 200:
        result = response.json()
        ai_message = result["choices"][0]["message"]["content"]
        return jsonify({"result": ai_message}) # 성공하면 AI 대답을 웹으로 보냄
    else:
        # 에러가 났을 때 어떤 에러인지 확인하기 위해 상태 코드를 추가했습니다.
        return jsonify({"result": f"주모가 파업했소. (에러코드: {response.status_code})"}), 500

# 4. 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
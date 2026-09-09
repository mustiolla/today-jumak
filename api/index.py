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
    사용자가 지역과 맛을 알려주면, 고민하거나 되묻지 말고 **즉시** 아래 규칙에 따라 추천 결과만 말하세요.

    [절대 지켜야 할 규칙]
    1. 🚫 절대 질문하지 마세요. (예: "어떤 걸 원하소?", "어느 쪽이오?" 등 질문 형태의 문장 절대 금지)
    2. 사용자가 말한 지역에서 생산되거나, 그 지역과 가장 잘 어울리는 막걸리 딱 1개를 주모가 알아서 확정해버리세요.
    3. 그 막걸리에 어울리는 안주도 1~2개 확정해서 추천하세요.
    4. 서울에서 구입 가능한지 여부도 알려주세요.
    5. 말투는 "~했소", "~구려", "아이고 손님!" 같은 사극 주모 톤을 쓰세요.
    6. 막걸리와 안주 이름은 반드시 <strong>막걸리이름</strong> 처럼 HTML 태그로 감싸세요.

    [출력 예시 - 이 흐름대로만 대답하세요]
    아이고 손님! 그 지역의 그런 맛을 찾으시는구려! 그렇다면 내가 <strong>(추천 막걸리)</strong>를 내어 드리겠소. 이놈이랑은 <strong>(추천 안주)</strong>가 찰떡궁합이지! 서울에서도 (구할 수 있소/구하기 어렵소). 얼른 한잔 들이켜 보시오!
    """

    url = "https://copa.codyssey.kr/v1/chat/completions"
    
    # 🚨 수정됨: API 키를 코드에 직접 적지 않고, Vercel 환경변수에서 안전하게 가져옵니다!
    import os
    api_key = os.environ.get('OPENAI_API_KEY')
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {
        "model": "gpt-5-mini",  # 🚨 수정됨: 존재하는 모델 이름으로 변경!
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
        return jsonify({"result": ai_message})
    else:
        return jsonify({"result": f"주모가 파업했소. (에러코드: {response.status_code})"}), 500

# 4. 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
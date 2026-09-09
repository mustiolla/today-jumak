import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# 1. Flask 앱 만들기 (서버 역할)
app = Flask(__name__)

# 2. 프론트엔드(JS)가 찾아올 주소(라우터) 열어주기
@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        # 3. 사용자가 화면에서 입력한 데이터(지역, 맛) 받아오기
        user_data = request.get_json()
        region = user_data.get('region', '전국')
        taste = user_data.get('taste', '맛있는')

        # 4. AI 주모 프롬프트
        system_instruction = """
당신은 한국의 전통 주막을 운영하는 친근하고 호탕한 '주모'입니다.
사용자가 원하는 지역과 맛을 알려주면, 고민하거나 되묻지 말고 즉시 아래의 [절대 지켜야 할 규칙]과 [출력 예시]에 맞춰 4개 문단 형식으로 답변을 내어주세요.

[절대 지켜야 할 규칙]
1. 🚫 되묻기 금지: 사용자에게 어떤 것을 원하는지 되묻거나 질문하지 마세요 (마지막 맺음말 "손님, 술상 차려드릴까 하오." 제외).
2. 실제 존재하는 전통주: 반드시 사용자가 요청한 지역(또는 인근)에서 생산되는 '실제로 존재하는' 막걸리 딱 1개만 확정 추천하세요. 가상의 술 이름을 절대 지어내지 마세요.
3. 막걸리 맛 설명: 첫맛, 탄산감, 목넘김, 피니시 등 구체적인 특징과 지역과의 조화를 풍부하게 설명하세요.
4. 페어링 안주: 해당 막걸리와 어울리는 안주 2가지를 확정하고, 각각 왜 잘 어울리는지 구체적인 궁합 이유를 설명하세요.
5. 판매처 및 구매 가능 여부: 서울/수도권 등 외지에서 구입 가능한지 여부를 솔직하게 알려주세요 (예: 대형마트나 전통주점에서 쉽게 구할 수 있는지, 아니면 지역 현지에서만 구할 수 있어 서울에서 구하기 어려운지).
6. 말투: 친근하고 구수한 사극 주모 말투('~했소', '~구려', '~추천하겠소', '~어울리오', '~안성맞춤이오', '~제격이오', '아이고 손님!')를 일관되게 사용하세요.
7. HTML 태그 필수: 추천하는 막걸리 이름과 안주 이름은 반드시 <b>이름</b> 태그로 감싸서 강조하세요. (마크다운 ** 대신 반드시 <b>태그 사용)
8. 문단 구분: 반드시 총 4개의 문단으로 구성하며, 각 문단 사이에는 빈 줄(줄바꿈 2번)을 넣으세요.

[출력 예시 - 반드시 아래의 4개 문단 구조와 줄바꿈, 어투 흐름을 그대로 따르세요]
아이고 손님! 속초 풍미를 품은 달달하고 탄산이 도드라지며 담백한 맛을 찾으신다구려, 주모가 바로 한 가지 고르고 안주도 함께 내오겠소.

막걸리로는 <b>설악산 막걸리</b>를 추천하겠소. 달큰한 감미가 먼저 오고 입안에서 톡톡 터지는 탄산감이 청량하며, 뒤끝은 깔끔하고 담백하게 정리되는 스타일이라 속초의 산해진미와 잘 맞소.

어울리는 안주는 한 가지 더 준비했소:
- <b>황태구이</b> ㅡ 담백하고 고소한 맛이 막걸리의 단맛과 궁합이 좋소.
- <b>해물파전</b> ㅡ 해물의 감칠맛과 파전의 기름짐을 탄산이 쏘~ 하고 정리해 주니 안성맞춤이오.

판매처 관련해선 정확치 않아 확답하기 어렵소. 현재, 서울에서 구입 가능하지 않소. 그래도 속초 여행길에 한 사발 들이키시면 제격이오. 손님, 술상 차려드릴까 하오.
"""

        url = "https://copa.codyssey.kr/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        # 🚨 주의: gpt-5-mini는 아직 없는 모델이라 에러가 날 수 있습니다. gpt-4o-mini로 수정했습니다!
        data = {
            "model": "gpt-5-mini", 
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"{region} 지역의 {taste} 맛이 나는 막걸리 추천해 주시오!"}
            ]
        }

        # 5. 교육장 서버로 요청 보내기
        response = requests.post(url, headers=headers, json=data)

        # 6. 결과 확인 및 프론트엔드로 돌려보내기
        if response.status_code == 200:
            result_data = response.json()
            ai_message = result_data["choices"][0]["message"]["content"]
            
            # HTML 화면에 띄울 수 있도록 JSON 형태로 변환해서 반환 (매우 중요!)
            return jsonify({"result": ai_message})
        else:
            return jsonify({"result": f"주모가 파업했소. (에러코드: {response.status_code})"}), 500

    except Exception as e:
        return jsonify({"result": f"주막에 불이 났소! ({str(e)})"}), 500

# 로컬 테스트용 코드 (Vercel에서는 무시됨)
if __name__ == '__main__':
    app.run(debug=True)
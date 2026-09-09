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
        너는 한국의 전통주를 꿰뚫고 있는 친근한 주막의 주모야.
        [엄격한 규칙]
        1. 반드시 '실제로 존재하는' 막걸리만 추천할 것. 절대 가상의 이름을 지어내지 마.
        2. 추천한 막걸리와 찰떡궁합인 안주를 한개 또는 두개 같이 추천해 줘.
        3. 말투는 "~했소", "~어떠소?" 같은 친근하고 구수한 사극 톤을 사용해. 다만, 너무 과하지 않게 자연스럽게 해줘.
        """

        url = "https://copa.codyssey.kr/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        # 🚨 주의: gpt-5-mini는 아직 없는 모델이라 에러가 날 수 있습니다. gpt-4o-mini로 수정했습니다!
        data = {
            "model": "gpt-4o-mini", 
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
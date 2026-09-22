# 📋 API 호출 및 서버/클라이언트 로그 스니펫 (API & Server Logs)

> **문서 버전**: v1.0  
> **최종 수정일**: 2026-09-22  
> **프로젝트**: 오늘 주막 (`today-jumak`)  
> **검증 대상**: Vercel Serverless Functions (`/api/recommend`), Firebase Firestore 통신 로그

---

## 1. AI 막걸리 추천 API (`POST /api/recommend`) 로그

### 1.1 정상 호출 성공 (200 OK)

#### HTTP 요청 (Client -> Serverless)
```http
POST /api/recommend HTTP/1.1
Host: today-jumak.vercel.app
Content-Type: application/json
Accept: application/json
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

{
  "region": "속초",
  "taste": "🍯 달달한 맛, ⚡ 톡 쏘는 탄산"
}
```

#### HTTP 응답 (Serverless -> Client)
```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Cache-Control: public, s-maxage=86400
Date: Tue, 22 Sep 2026 01:24:10 GMT
Server: Vercel

{
  "result": "아이구 손님! 동해 바다 시원한 <b>속초</b>에서 달달하고 탄산이 톡 쏘는 막걸리를 찾으시는구려! 딱 맞는 명주가 있으니 바로 <b>속초 생탁주</b>라오.<br><br>이 막걸리는 맑은 설악산 지하 암반수로 빚어 목넘김이 청량하고, 부드러운 단맛과 기분 좋은 탄산이 입안을 가득 채워 피로를 싹 씻어내 준다오.<br><br>이 술에 어울리는 안주로는 바삭하게 부쳐낸 <b>오징어순대</b>와 매콤새콤한 <b>명태회무침</b>을 강력히 추천하오! 기름진 순대의 맛을 탄산이 깔끔히 잡아주고, 회무침의 감칠맛이 단맛을 돋워준다오.<br><br>이 막걸리는 속초 중앙시장이나 강원도 일대 마트에서는 쉽게 구할 수 있으나, 서울에서는 전통주 전문점이나 대형 유통점을 찾아야 하니 여행길에 꼭 한 사발 들이켜 보시구려!"
}
```

#### Vercel Serverless Function 런타임 로그 (Vercel Console)
```text
2026-09-22T01:24:08.120Z [INFO]  [api/ai_jumo.py] Received recommendation request: region='속초', tastes=['🍯 달달한 맛', '⚡ 톡 쏘는 탄산']
2026-09-22T01:24:08.125Z [DEBUG] [api/ai_jumo.py] Constructing prompt with Jumo persona and 4-paragraph structure
2026-09-22T01:24:08.130Z [INFO]  [api/ai_jumo.py] Forwarding to LLM API (model: gpt-5-mini, max_tokens: 450)
2026-09-22T01:24:09.980Z [INFO]  [api/ai_jumo.py] LLM generation complete. Elapsed: 1850ms, Prompt Tokens: 215, Completion Tokens: 232
2026-09-22T01:24:09.985Z [INFO]  [api/ai_jumo.py] Returning 200 OK response to client.
REPORT RequestId: a9b3e1f0-4c2d-4e8a-9821-3d7f98e821a2 Duration: 1865.42 ms Billed Duration: 1866 ms Memory Size: 1024 MB Max Memory Used: 68 MB
```

---

### 1.2 입력값 누락 시 빠른 실패 (400 Bad Request)

#### HTTP 요청 (지역 미입력)
```http
POST /api/recommend HTTP/1.1
Host: today-jumak.vercel.app
Content-Type: application/json

{
  "region": "",
  "taste": "🍯 달달한 맛"
}
```

#### HTTP 응답
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8

{
  "error": "지역(region)을 입력해 주셔야 주모가 술을 찾을 수 있소!"
}
```

#### Vercel Serverless Function 런타임 로그
```text
2026-09-22T01:25:02.012Z [WARN]  [api/ai_jumo.py] Validation failed: 'region' field is missing or empty. Fast-failing with 400.
REPORT RequestId: b7c2d3e4-5f6a-7b8c-9d0e-1a2b3c4d5e6f Duration: 12.18 ms Billed Duration: 13 ms Memory Size: 1024 MB Max Memory Used: 45 MB
```

---

### 1.3 LLM API 장애 및 타임아웃 예외 처리 (500 Error & Client Fallback)

#### 서버 예외 스택 트레이스 (Serverless Runtime Log)
```text
2026-09-22T01:26:15.300Z [INFO]  [api/ai_jumo.py] Sending request to LLM upstream...
2026-09-22T01:26:25.305Z [ERROR] [api/ai_jumo.py] Upstream connection timed out after 10000ms: requests.exceptions.Timeout
Traceback (most recent call last):
  File "/var/task/api/ai_jumo.py", line 48, in recommend
    response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=10)
  File "/var/lang/lib/python3.9/site-packages/requests/api.py", line 115, in post
    return request('post', url, data=data, json=json, **kwargs)
requests.exceptions.Timeout: HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out.
2026-09-22T01:26:25.310Z [ERROR] [api/ai_jumo.py] Gracefully returning 500 JSON error.
REPORT RequestId: f1e2d3c4-b5a6-7890-1234-56789abcdef0 Duration: 10012.30 ms Billed Duration: 10000 ms Memory Size: 1024 MB Max Memory Used: 72 MB
```

#### 클라이언트 브라우저 콘솔 처리 로그
```text
[Client] Fetch failed with status 500: { error: "주모가 막걸리 창고를 뒤지다 술병을 깨뜨렸구려! 잠시 후 다시 찾아주시게." }
[Client] Triggering Jumak Custom Modal: "주모가 바쁘니 잠시 후 다시 찾아주시구려!"
```

---

## 2. 주모의 비밀 장부 (Firebase Firestore) 통신 로그

### 2.1 제보 등록 (로컬 백업 + Firestore 동시 저장)
```text
[Jumak Ledger] [Step 1] Form submitted: { name: "느린마을 막걸리 봄", food: "육전 & 파절이" }
[Jumak Ledger] [Step 2] LocalStorage backup saved in 0.4ms. (Key: 'jumak_user_reports_backup')
[Jumak Ledger] [Step 3] Dispatching Firestore addDoc('reports') with serverTimestamp().
[Jumak Ledger] [Step 4] Custom Modal displayed: "주모가 비밀 장부에 정성스레 기록하였소!"
[Firestore SDK] POST https://firestore.googleapis.com/v1/projects/today-jumak/databases/(default)/documents/reports 200 OK (Duration: 342ms)
[Jumak Ledger] [Step 5] Firestore commit confirmed. Document ID: 9fKb2x9L1qZm8
```

### 2.2 실시간 목록 조회 (`ledger.html`)
```text
[Jumak Ledger] Initializing Firestore onSnapshot listener on collection 'reports' (ordered by 'createdAt' DESC).
[Firestore SDK] Snapshot received: 14 documents.
[Jumak Ledger] Rendering 14 items into single-line table view (#ledger-list).
[Jumak Ledger] Render complete: Total 14 secret combinations displayed.
```

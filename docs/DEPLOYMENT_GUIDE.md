# 🚀 배포 및 운영 가이드: 실패 사례, 로그 모니터링 & 재배포 체크리스트

> **문서 버전**: v1.0  
> **최종 수정일**: 2026-09-22  
> **호스팅 플랫폼**: Vercel + GitHub  
> **백엔드 런타임**: Python 3.9+ (Vercel Serverless Functions)

---

## 1. 개요 및 Vercel 배포 파이프라인

`today-jumak` 서비스는 GitHub 저장소의 `main` 브랜치에 변경 사항이 Push되면, Vercel CI/CD 파이프라인이 이를 자동으로 감지하여 **정적 웹 페이지(`index.html`, `ledger.html`)**와 **Python Serverless 함수(`api/ai_jumo.py`)**를 빌드 및 배포합니다.

```mermaid
flowchart LR
    A["GitHub Push<br/>(main 브랜치)"] --> B["Vercel Build<br/>- requirements.txt 설치<br/>- vercel.json 라우팅 구성"]
    B --> C["Serverless 배포<br/>- 글로벌 CDN 캐싱<br/>- Lambda 함수 프로비저닝"]
    C --> D["🌐 라이브 서비스<br/>today-jumak.vercel.app"]
```

---

## 2. 배포 실패 대표 사례 Top 5 및 해결 방안 (Failure Cases & Fixes)

실제 서버리스 배포 과정에서 발생할 수 있는 주요 실패 사례와 해결 가이드입니다.

### ❌ 사례 1: Python 의존성 설치 실패 (`Build Failed`)
- **증상**: Vercel 빌드 도중 `pip install` 단계에서 빌드가 중단되거나 `ModuleNotFoundError: No module named 'flask'` 발생.
- **원인**: 최상위 디렉토리에 `requirements.txt`가 누락되었거나, 패키지 버전이 서버리스 Python 런타임과 비호환되는 경우.
- **해결 방안**:
  ```text
  # requirements.txt 파일 필수 패키지 명시
  Flask>=2.0.0
  requests>=2.28.0
  ```
  불필요하게 무거운 C 확장 라이브러리를 제외하고 순수 파이썬 패키지 위주로 구성.

---

### ❌ 사례 2: 환경 변수 누락으로 인한 500 서버 에러 (`FUNCTION_INVOCATION_FAILED`)
- **증상**: 배포(빌드)는 성공했으나 웹에서 "주모! 추천해 주시오" 클릭 시 `500 Internal Server Error` 발생.
- **원인**: Vercel 대시보드에 `OPENAI_API_KEY` 환경 변수가 등록되지 않아 `os.environ.get('OPENAI_API_KEY')`가 `None`을 반환.
- **해결 방안**:
  1. Vercel Dashboard > Project > **Settings** > **Environment Variables** 진입.
  2. Key: `OPENAI_API_KEY`, Value: `sk-...` 등록.
  3. **Deployments** 메뉴에서 최신 배포를 `Redeploy`하여 새 환경 변수 주입.

---

### ❌ 사례 3: `vercel.json` 라우팅 규칙 오류로 인한 404 에러
- **증상**: 프론트엔드에서 `/api/recommend`로 POST 요청 시 `404 Not Found` 반환.
- **원인**: `vercel.json`의 `rewrites` 또는 `routes` 설정에서 소스 경로(`src`)와 타겟 파일(`dest`) 경로가 불일치.
- **해결 방안**:
  ```json
  {
    "rewrites": [
      {
        "source": "/api/recommend",
        "destination": "/api/ai_jumo.py"
      }
    ]
  }
  ```
  정적 파일(`ledger.html`)과 API 엔드포인트의 라우팅 충돌 방지.

---

### ❌ 사례 4: Serverless 실행 시간 초과 (`504 Gateway Timeout`)
- **증상**: 주모의 답변 생성이 10초 이상 지연되면서 브라우저에 `504 Gateway Timeout` 반환.
- **원인**: Vercel Hobby 티어의 서버리스 함수 기본 실행 시간 제한은 **10초**입니다. LLM API 트래픽 폭주 시 10초를 초과할 수 있음.
- **해결 방안**:
  1. 프롬프트의 `max_tokens`를 450 이하로 축소하여 LLM 생성 시간 단축.
  2. `vercel.json`에 함수별 `maxDuration` 설정 (Pro 티어 기준 최대 60초까지 확장 가능):
     ```json
     {
       "functions": {
         "api/*.py": { "maxDuration": 15 }
       }
     }
     ```

---

### ❌ 사례 5: 리눅스 배포 환경의 파일명 대소문자 불일치
- **증상**: Windows 로컬에서는 `ledger.html`이 잘 열리지만 배포 사이트에서는 `404` 발생.
- **원인**: Windows는 파일명 대소문자를 구분하지 않지만, Vercel 빌드 머신(Linux)은 대소문자를 엄격히 구분함 (`Ledger.html` vs `ledger.html`).
- **해결 방안**: Git 파일명을 모두 소문자로 일치시키고 `git mv` 명령어로 변경 내역 커밋.

---

## 3. Vercel 로그 및 콘솔 모니터링 방법 (Monitoring & Logs)

### 3.1 웹 콘솔을 통한 실시간 로그 확인
1. [Vercel 대시보드](https://vercel.com/) 접속 후 `today-jumak` 프로젝트 선택.
2. 상단 메뉴에서 **Logs** 탭 클릭.
3. 필터링 활용:
   - **Level**: `Error`만 필터링하여 500 에러 및 예외 스택 트레이스 즉시 확인.
   - **Timeline**: 특정 시점의 호출 로그 추적.
4. 함수 상세 정보 확인:
   - `Duration`: 함수 실행 시간 (ms 단위)
   - `Memory Used`: 메모리 점유율 (MB 단위)
   - `Status`: 200 OK, 400 Bad Request, 500 Error 등.

### 3.2 Vercel CLI를 통한 터미널 로그 스트리밍
```bash
# 실시간 프로덕션 로그 스트리밍
vercel logs today-jumak.vercel.app --follow

# 특정 에러 로그만 필터링
vercel logs today-jumak.vercel.app --output=raw | grep "ERROR"
```

---

## 4. 10단계 재배포 체크리스트 (Redeployment 10-Point Checklist)

안전하고 무결점인 재배포를 위해 배포 전/후 다음 10가지 항목을 반드시 점검합니다.

| 단계 | 점검 항목 | 점검 방법 | 상태 |
| :---: | :--- | :--- | :---: |
| **사전 1** | `.gitignore`에 `.env` 및 민감 정보가 정상 등록되어 있는가? | `git status`로 `.env` 미노출 확인 | ✅ 완료 |
| **사전 2** | `requirements.txt`에 필요한 패키지가 모두 명시되어 있는가? | 로컬 가상환경 설치 테스트 | ✅ 완료 |
| **사전 3** | `vercel.json`의 라우팅 설정(`rewrites`) 문법이 올바른가? | JSON 유효성 검사 | ✅ 완료 |
| **사전 4** | 로컬 환경에서 `vercel dev`로 AI 추천 및 장부 조회가 정상 작동하는가? | 로컬 브라우저 E2E 테스트 | ✅ 완료 |
| **사전 5** | 불필요한 임시 파일이나 디버그용 `console.log`가 정리되었는가? | 코드 리뷰 | ✅ 완료 |
| **배포 6** | Git 커밋 메시지가 변경 사항을 명확히 설명하는가? | `git log -n 1` 확인 | ✅ 완료 |
| **배포 7** | Vercel 대시보드에서 빌드 상태가 `Ready (Green)`로 완료되었는가? | Vercel Deployments 화면 확인 | 배포 시 |
| **사후 8** | 배포된 라이브 URL([today-jumak.vercel.app](https://today-jumak.vercel.app))이 정상 접속되는가? | 브라우저 직접 접속 | 배포 시 |
| **사후 9** | 라이브 사이트에서 AI 추천 요청 시 주모 답변이 정상 출력되는가? | 실제 추천 1회 실행 | 배포 시 |
| **사후 10**| 비밀 장부(`ledger.html`)에 실시간 제보가 정상 조회되는가? | 장부 페이지 접속 확인 | 배포 시 |

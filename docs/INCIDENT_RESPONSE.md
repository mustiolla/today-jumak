# 🚨 API 키 유출 시 긴급 대응 매뉴얼 (Incident Response Manual)

> **문서 버전**: v1.0  
> **최종 수정일**: 2026-09-22  
> **적용 대상**: `today-jumak` 프로젝트 (`OPENAI_API_KEY`, Firebase Config 등)  
> **책임자**: 보안 및 인프라 담당자

---

## 1. 개요 및 인시던트 정의

API 키(특히 OpenAI API Key)가 GitHub 공개 저장소, 클라이언트 사이드 코드, 블로그 또는 외부 커뮤니티에 노출될 경우, 악의적인 봇에 의해 수 분 내로 수백~수천 달러의 과금이 발생하거나 계정이 정지될 수 있습니다.  
본 매뉴얼은 **API 키 유출 발생 시 즉시 실행해야 하는 4단계 대응 절차**, **로그 조사 방법**, 그리고 **재발 방지 체크리스트**를 정의합니다.

---

## 2. 긴급 대응 4단계 절차 (Phase 1 ~ Phase 4)

```mermaid
flowchart LR
    P1["1단계: 즉시 폐기 (Revoke)"] --> P2["2단계: 새 키 교체 & 배포 (Rotate)"]
    P2 --> P3["3단계: 로그 조사 & 피해 산정 (Audit)"]
    P3 --> P4["4단계: 재발 방지 조치 (Prevent)"]
```

### 🚨 1단계: 유출 키 즉시 폐기 (Immediate Revocation) - 소요 시간: 1분 이내
*목표: 유출된 키의 추가 호출을 0초 만에 차단*

1. **OpenAI API 키 폐기**:
   - [OpenAI API Keys 대시보드](https://platform.openai.com/api-keys) 접속.
   - 유출된 키 항목 우측의 **휴지통(Delete/Revoke) 아이콘** 클릭하여 즉시 비활성화.
   - *주의: 코드를 수정하기 전에 대시보드에서 키를 먼저 폐기해야 실시간 과금을 막을 수 있습니다.*
2. **Firebase/기타 서비스 보안 규칙 확인**:
   - Firebase 콘솔에서 Firestore Security Rules가 비인가 읽기/쓰기를 차단하고 있는지 점검.

---

### 🔑 2단계: 신규 키 발급 및 Vercel 환경 변수 교체 (Rotate & Redeploy) - 소요 시간: 3분 이내
*목표: 서비스 정상화를 위한 새 키 반영*

1. **새로운 API Key 생성**:
   - OpenAI 대시보드에서 `+ Create new secret key` 클릭.
   - 키 이름 지정 (예: `today-jumak-prod-20260922`) 및 권한 범위(Permissions) 설정.
2. **Vercel 환경 변수 즉시 갱신**:
   - **방법 A (웹 대시보드)**: Vercel Project > Settings > Environment Variables > `OPENAI_API_KEY` 값 Edit 후 Save.
   - **방법 B (CLI)**:
     ```bash
     # 기존 키 삭제 및 새 키 추가
     vercel env rm OPENAI_API_KEY production -y
     vercel env add OPENAI_API_KEY production
     # 프롬프트에 새로운 sk-... 입력
     ```
3. **무중단 재배포 트리거**:
   - Vercel Deployments 메뉴에서 최신 배포의 `Redeploy` 버튼 클릭하여 즉시 새 환경 변수 반영.

---

### 🔍 3단계: 로그 조사 및 피해 규모 파악 (Audit & Impact Assessment) - 소요 시간: 10분 이내
*목표: 비정상 호출 여부, 토큰 소모량, 접근 IP 조사*

#### 3.1 OpenAI 사용량 및 활동 로그 분석
1. [OpenAI Usage 대시보드](https://platform.openai.com/usage) 접속.
2. **시간대별 토큰 소모량(Requests / Tokens)** 확인:
   - 유출 시점 전후로 스파이크(비정상 급증)가 발생했는지 확인.
   - 호출된 모델명(`gpt-4`, `gpt-3.5-turbo`, `gpt-5-mini` 등) 파악.
3. **비용 한도 및 결제 내역 확인**:
   - [Billing Overview](https://platform.openai.com/account/billing/overview)에서 유출 기간 동안 청구된 비용 확인.
   - **OpenAI 지원팀 문의**: 유출로 인한 악의적 과금 발생 시, [OpenAI Help Center](https://help.openai.com/)에 즉시 인시던트 리포트를 제출하고 환불/감면 요청.

#### 3.2 Vercel Serverless Function 런타임 로그 조사
1. [Vercel Dashboard](https://vercel.com/) > `today-jumak` 프로젝트 > **Logs** 탭 진입.
2. 필터 설정:
   - Status: `200`, `429 (Too Many Requests)`, `500`
   - Path: `/api/recommend`
3. 조사 항목:
   - **클라이언트 IP 및 국가**: 비정상적인 해외 IP 대량 호출 여부.
   - **User-Agent**: 스크립트 기반 크롤러(Python-requests, curl 등) 유입 여부.
   - **호출 빈도(RPS)**: 단위 시간당 비정상적인 반복 호출 발생 여부.

---

### 🧹 4단계: Git 히스토리 영구 제거 및 재발 방지 (Clean-up & Prevention)

#### 4.1 Git 커밋 히스토리에서 키 영구 박멸
GitHub에 이미 push된 경우, 단순히 키를 지우고 새로 commit하더라도 **과거 커밋 히스토리에 키가 영구히 남아있습니다.**

```bash
# 1. BFG Repo-Cleaner 또는 git-filter-repo 도구 사용
# git-filter-repo 설치
pip install git-filter-repo

# 2. 히스토리 전체에서 특정 문자열/키 패턴 치환 또는 .env 파일 기록 삭제
git filter-repo --invert-paths --path .env --force

# 3. 변경된 히스토리를 원격 저장소에 강제 푸시 (주의!)
git push origin main --force
```

#### 4.2 GitHub Secret Scanning 및 Push Protection 활성화
- 저장소 설정(`Settings` > `Code security and analysis`):
  - **Secret scanning**: Enabled (커밋 내 API 키 탐지 시 즉시 알림)
  - **Push protection**: Enabled (API 키가 포함된 커밋의 push 자체를 사전 차단)

---

## 3. 재발 방지 10대 보안 체크리스트 (Security Checklist)

| 번호 | 점검 항목 | 점검 주기 | 상태 |
| :---: | :--- | :---: | :---: |
| 1 | `.gitignore`에 `.env`, `.env.local`, `*.pem`, `serviceAccountKey.json`이 포함되어 있는가? | 상시 | ✅ 완료 |
| 2 | 클라이언트 사이드(`index.html`, `ledger.html`)에 백엔드 시크릿 키가 하드코딩되지 않았는가? | 배포 전 | ✅ 완료 |
| 3 | 모든 외부 LLM 호출은 백엔드 Serverless(`api/ai_jumo.py`) 프록시를 통해서만 이루어지는가? | 아키텍처 점검 | ✅ 완료 |
| 4 | GitHub 저장소의 **Secret Scanning** 및 **Push Protection**이 켜져 있는가? | 분기별 | 점검 권장 |
| 5 | OpenAI 계정에 **Usage Limits (Monthly Soft/Hard Limit)**가 설정되어 있는가? | 월 1회 | 점검 권장 |
| 6 | Git 커밋 전 `git diff --cached`를 통해 추가된 파일과 내용을 검토하는가? | 커밋 시 | 상시 준수 |
| 7 | 로컬 개발 환경용 `.env.example` 템플릿에 실제 키가 아닌 더미값(`sk-xxxx...`)만 들어있는가? | 변경 시 | ✅ 완료 |
| 8 | Firebase Firestore 보안 규칙(`rules`)에서 비인가 쓰기/대량 삭제가 방지되고 있는가? | 분기별 | 점검 권장 |
| 9 | Vercel의 환경 변수가 `Production`, `Preview`, `Development` 환경별로 분리되어 있는가? | 배포 시 | 점검 권장 |
| 10 | 팀원 간 API 키 공유 시 메신저 대신 보안 비밀번호 관리자(1Password, Bitwarden 등)를 사용하는가? | 상시 | 원칙 준수 |

---

## 4. 비상 연락망 및 보고 양식

- **보안 담당자**: `today-jumak` 관리자
- **보고 양식**:
  ```text
  [보안 사고 보고서]
  1. 사고 인지 일시: 2026-XX-XX HH:MM
  2. 유출 경로: (예: GitHub 커밋, 클라이언트 노출 등)
  3. 유출된 키 식별자: sk-... (앞 6자리, 뒤 4자리만 기록)
  4. 조치 현황: 키 폐기 완료 (HH:MM), 신규 키 발급 및 Vercel 갱신 완료 (HH:MM)
  5. 피해 규모: 비인가 호출 N건, 소모 비용 $X.XX
  6. 재발 방지 조치: Git 히스토리 BFG 정리 완료, Secret Scanning 활성화
  ```

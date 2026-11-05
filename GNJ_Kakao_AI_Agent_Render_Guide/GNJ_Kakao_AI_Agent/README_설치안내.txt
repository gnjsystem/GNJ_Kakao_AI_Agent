GNJ 카카오톡 AI 영업비서 - 초기 연동 서버

이 패키지는 카카오 챗봇 관리자센터의 스킬 요청을 받는 서버 초안입니다.
카카오톡 채널 자체나 카카오 챗봇을 자동으로 생성/배포하지는 않습니다.
공개 HTTPS 주소로 서버를 배포하고, 카카오 챗봇 관리자센터에서 스킬 URL을 등록해야 작동합니다.

[현재 포함]
- 카카오 스킬 API 형식(v2.0) 요청/응답 처리
- OpenAI Responses API 기반 한국어 GNJ 영업비서 대화
- 최초 관리자 연결코드 등록
- 영업처 저장: 영업처등록 기관명 | 상담내용 | 다음 행동
- 영업처 조회: 영업처목록
- 대화 문맥 저장 및 초기화
- 비관리자에게는 일반 고객 문의 안내만 제공

[아직 추가 개발 필요]
- 외부 웹 검색/기관 수요 데이터 수집
- 제안서 파일 생성 및 다운로드
- CRM 웹 관리자 화면
- 이메일 발송
- 자동 일정/알림
- 운영 보안 강화(관리자 계정 승인 절차, 접근 로그, 백업, 요청 검증)

[환경변수]
1. .env.example을 복사해 .env로 이름 변경
2. OPENAI_API_KEY에 발급한 API 키 입력
3. ADMIN_PAIR_CODE에 충분히 긴 임의의 비밀코드 입력
4. OPENAI_MODEL은 사용 가능한 API 모델명으로 지정
5. .env는 외부에 공유하거나 GitHub에 올리지 마세요.

[로컬 테스트]
Windows:
  py -3 -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app:app --host 0.0.0.0 --port 8000

상태 확인:
  http://localhost:8000/health

카카오 스킬 URL:
  https://배포한-도메인/kakao/skill
  반드시 HTTPS 공개 주소여야 합니다. localhost 주소는 카카오 서버에서 접근할 수 없습니다.

[카카오 관리자센터 설정 개요]
1. https://i.kakao.com 접속 및 로그인
2. 챗봇 관리자센터에서 카카오톡 챗봇 생성
3. 기존 지앤제이시스템 채널을 해당 봇에 연결
4. 스킬 메뉴에서 새 스킬 생성
5. URL에 https://배포도메인/kakao/skill 등록
6. 폴백 블록(또는 별도 AI 대화 블록)에 해당 스킬 연결
7. 테스트 후 배포

[관리자 등록]
채널 채팅방에서 다음 문장을 입력합니다.
관리자등록 여기에_설정한_ADMIN_PAIR_CODE

관리자 등록이 완료된 뒤 대표님 계정에서만 AI 영업비서 기능이 열립니다.
다른 이용자에게 관리자 연결코드를 절대 공유하지 마세요.
관리자 등록을 마친 후에는 서버 로그/접근통제를 점검하고 코드를 교체하는 것을 권장합니다.

[중요한 카카오 정책/동작]
- 카카오톡 채널과 챗봇은 별도 설정이며, 기존 채널에 챗봇을 연결하고 배포해야 합니다.
- 스킬 서버는 카카오 봇 시스템에서 HTTP POST JSON을 받는 공개 API입니다.
- 채널은 공개 고객 접점입니다. 이 패키지는 관리자 외 이용자에게 일반 상담 안내만 응답하도록 구성했습니다.
- 카카오 챗봇 Event API로 먼저 알림을 보내는 기능은 별도 구현·월렛·과금 확인이 필요합니다.
- 대표님이 개인 비서로 쓰려는 목적이라면 관리자 식별키 등록과 비관리자 응답 분리가 중요합니다.

공식 문서:
카카오 챗봇 스킬 만들기:
https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/make_skill
스킬 요청/응답 JSON:
https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/answer_json_format
챗봇 튜토리얼:
https://kakaobusiness.gitbook.io/main/tool/chatbot/tutorial/make_chatbot/tutorial_3

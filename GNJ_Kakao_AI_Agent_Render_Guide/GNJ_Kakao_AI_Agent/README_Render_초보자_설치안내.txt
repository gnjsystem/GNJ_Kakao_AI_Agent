GNJ 카카오톡 AI 영업비서 - Render 배포 초보자 안내
==================================================

중요
- 이 파일은 서버 프로그램입니다. 카카오 챗봇이나 카카오톡 채널을 자동으로 만들지는 않습니다.
- Render에 배포하고 HTTPS 주소를 받은 뒤, 카카오 챗봇 스킬 URL에 등록해야 합니다.
- OpenAI API 사용료와 Render 서버 이용료는 별도입니다.
- API 키/관리자 연결코드는 절대 카카오톡 대화나 공개 GitHub 저장소에 올리지 마세요.

1. 준비물
- GitHub 계정
- Render 계정
- OpenAI API 키 (ChatGPT 구독과 API 과금은 별도)
- 카카오 챗봇 관리자센터 계정

2. 압축 풀기
- GNJ_Kakao_AI_Agent_Starter.zip 압축을 풉니다.
- GNJ_Kakao_AI_Agent 폴더 안에 app.py, requirements.txt, Procfile,
  render.yaml, .gitignore 파일이 있는지 확인합니다.

3. GitHub에 비공개 저장소 만들기
- https://github.com 접속 후 로그인합니다.
- New repository를 선택합니다.
- Repository name: GNJ_Kakao_AI_Agent
- Private를 선택합니다.
- Create repository를 누릅니다.
- 압축을 푼 폴더 안의 파일들을 저장소 최상위(root)에 업로드합니다.
  주의: 폴더 자체를 한 단계 더 중첩해서 올리지 말고 app.py가 저장소 첫 화면에 보여야 합니다.
- .env 파일이나 API 키는 업로드하지 않습니다.

4. Render에 서버 만들기
- https://render.com 접속 후 로그인합니다.
- New + > Blueprint를 선택합니다.
- GitHub 계정을 연결하고 방금 만든 GNJ_Kakao_AI_Agent 저장소를 선택합니다.
- render.yaml을 읽어 서비스 설정이 표시되면 적용합니다.
- 저장소를 찾지 못하면 GitHub 연결 권한에서 해당 Private 저장소 접근을 허용합니다.

5. 환경변수 입력
Render 대시보드에서 생성된 서비스 > Environment 메뉴에서 다음 값을 입력합니다.
- OPENAI_API_KEY = 본인의 OpenAI API 키
- OPENAI_MODEL = OpenAI API 계정에서 실제 사용 가능한 모델명
- ADMIN_PAIR_CODE = 본인이 정한 길고 임의적인 비밀코드

예시 형식(실제 키가 아님):
ADMIN_PAIR_CODE = GNJ-관리자-임의문자열-길게

중요:
- API 키와 관리자 코드를 이 대화에 보내지 마세요.
- OPENAI_MODEL에 임의의 모델명을 넣지 말고 API 계정에서 사용 가능한 모델명을 확인하세요.
- DB_PATH는 render.yaml에서 /var/data/gnj_kakao.db로 지정되어 있습니다.
- render.yaml은 영구 디스크를 포함하는 구성이므로 Render에서 유료 인스턴스/디스크 비용이 발생할 수 있습니다.
  실제 운영 전 요금 화면을 확인하고 승인하세요.

6. 배포 확인
- Render 서비스의 Events/Logs에서 Deploy successful 또는 Live 상태를 확인합니다.
- 서비스 주소를 열어 /health를 붙여 접속합니다.
  예: https://내-서비스이름.onrender.com/health
- 정상이라면 다음과 비슷한 JSON이 표시됩니다.
  {"status":"ok","service":"GNJ Kakao AI Assistant"}

7. 카카오 스킬 URL 등록
- 카카오 챗봇 관리자센터 https://i.kakao.com 접속
- GNJ 챗봇 선택 > 스킬 > 생성한 GNJ_AI_Sales_Skill 선택
- URL에 다음 주소 입력:
  https://내-서비스이름.onrender.com/kakao/skill
- 저장 후 스킬 테스트를 진행합니다.

8. 폴백 블록 연결
- 시나리오 > 기본 시나리오 > 폴백 블록
- 파라미터 설정에서 GNJ_AI_Sales_Skill 선택
- 봇 응답에서 스킬데이터 선택
- 저장 후 테스트합니다.

9. 관리자 등록
카카오 채널 1:1 채팅방에서 다음 형식으로 입력합니다.
관리자등록 본인이_설정한_ADMIN_PAIR_CODE

정상 등록 응답을 확인한 뒤에는 관리자 연결코드를 바꾸거나 재사용하지 않는 것이 좋습니다.
관리자 코드가 외부에 노출되었다면 즉시 교체하고 서버를 재배포하세요.

10. 꼭 알아둘 제한
- Render 무료 웹서비스는 유휴 상태에서 중단될 수 있고, 로컬 파일이 재배포/재시작 때 사라질 수 있습니다.
- 이 프로그램은 영업처/대화 기록을 SQLite에 저장합니다. 운영 데이터 보존을 위해 영구 디스크 또는 별도 관리형 DB가 필요합니다.
- 현재 초기 버전에는 실시간 웹 검색, 기관 구매계획 자동 수집, 이메일 자동 발송, 자동 알림, CRM 웹 화면이 포함되어 있지 않습니다.
- 카카오 챗봇 응답시간 제한을 고려해 실제 운영 테스트를 충분히 해야 합니다.

공식 안내:
Render Web Services: https://render.com/docs/web-services
Render Environment Variables: https://render.com/docs/configure-environment-variables
Render Free 제한: https://render.com/docs/free

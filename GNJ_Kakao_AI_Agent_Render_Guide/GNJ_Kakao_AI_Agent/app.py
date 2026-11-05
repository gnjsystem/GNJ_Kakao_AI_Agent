import os, sqlite3, logging, time
from datetime import datetime
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gnj-kakao-ai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()
ADMIN_PAIR_CODE = os.getenv("ADMIN_PAIR_CODE", "").strip()
DB_PATH = os.getenv("DB_PATH", "gnj_kakao.db")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="GNJ Kakao AI Sales Assistant", version="0.1.0")

SYSTEM_PROMPT = """
당신은 지앤제이시스템(GNJ System)의 전담 AI 영업본부장이다. 한국어로 답한다.
전북 기반 1인 B2B 납품·유통·시공 및 렌탈 사업을 지원한다.
취급 분야: LG·삼성 등 가전, 시스템에어컨·냉난방기, 전자칠판·TV·모니터,
컴퓨터·IT, 주방가전, 상업용/생활가전, 렌탈·장기구독.
고객: 지자체, 학교, 교육기관, 군부대, 공공기관, 병원·복지시설, 기업, 프랜차이즈.
입찰은 보조 영업경로이지 핵심이 아니다. 대표자는 1인 사업자이므로 저비용·고효율·협력업체 활용을 우선한다.
학교 HVAC는 기존 전문 시공·설계·기계설비 업체와 협력하는 접근을 우선 검토한다.
제조사/렌탈사의 A/S와 정기 관리 주체를 구분한다.
확인되지 않은 구매계획·담당자·예산·가격·실적을 만들어내지 않는다.
이 초기 버전은 실시간 웹 검색이 연결되지 않았으므로 최신 조사 요청에는 한계를 알리고 근거를 지어내지 않는다.
제안서·메일은 초안으로 작성하며 사용자 승인 없이 발송·계약 등 외부 행동을 하지 않는다.
확인된 사실과 추정을 구분하고, 실행 가능한 다음 행동을 구체적으로 제시한다.
"""

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS admins(
            kakao_user_id TEXT PRIMARY KEY, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS leads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization TEXT NOT NULL, details TEXT, next_action TEXT,
            stage TEXT DEFAULT '신규', created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kakao_user_id TEXT NOT NULL, role TEXT NOT NULL,
            content TEXT NOT NULL, created_at TEXT NOT NULL)""")

def is_admin(uid: str) -> bool:
    if not uid:
        return False
    with db() as c:
        return c.execute("SELECT 1 FROM admins WHERE kakao_user_id=?", (uid,)).fetchone() is not None

def remember(uid: str, role: str, content: str):
    with db() as c:
        c.execute("INSERT INTO history(kakao_user_id,role,content,created_at) VALUES(?,?,?,?)",
                  (uid, role, content[:10000], datetime.now().isoformat(timespec="seconds")))
        c.execute("""DELETE FROM history WHERE kakao_user_id=? AND id NOT IN
                  (SELECT id FROM history WHERE kakao_user_id=? ORDER BY id DESC LIMIT 16)""", (uid,uid))

def get_history(uid: str):
    with db() as c:
        rows = c.execute("SELECT role,content FROM history WHERE kakao_user_id=? ORDER BY id DESC LIMIT 10",
                         (uid,)).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def kakao_text(text: str):
    # Kakao Skill response v2.0; keep within a conservative text size.
    return JSONResponse({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": (text or "요청을 처리하지 못했습니다.")[:950]}}]
        }
    })

def extract_user(payload: dict[str, Any]):
    user = (payload.get("userRequest") or {}).get("user") or {}
    return str(user.get("id") or user.get("properties", {}).get("botUserKey") or "")

def extract_utterance(payload: dict[str, Any]):
    return str((payload.get("userRequest") or {}).get("utterance") or "").strip()

def save_lead(raw: str):
    parts = [p.strip() for p in raw.split("|")]
    if not parts or not parts[0]:
        return "형식: 영업처등록 기관명 | 상담내용 | 다음 행동"
    with db() as c:
        cur = c.execute(
            "INSERT INTO leads(organization,details,next_action,created_at) VALUES(?,?,?,?)",
            (parts[0], parts[1] if len(parts)>1 else "",
             parts[2] if len(parts)>2 else "", datetime.now().isoformat(timespec="seconds"))
        )
        lead_id = cur.lastrowid
    return f"영업처를 저장했습니다.\n번호: #{lead_id}\n기관: {parts[0]}"

def list_leads():
    with db() as c:
        rows = c.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 8").fetchall()
    if not rows:
        return "저장된 영업처가 없습니다."
    return "\n\n".join(
        f"#{r['id']} {r['organization']} [{r['stage']}]\n내용: {r['details'] or '-'}\n다음 행동: {r['next_action'] or '-'}"
        for r in rows
    )

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "service": "GNJ Kakao AI Assistant"}

@app.post("/kakao/skill")
async def kakao_skill(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return kakao_text("요청 형식이 올바르지 않습니다.")

    uid = extract_user(payload)
    utterance = extract_utterance(payload)

    if not uid:
        return kakao_text("사용자 식별 정보를 확인할 수 없습니다. 채널 관리자에게 문의해 주세요.")

    # The public channel is not automatically an admin-only private chat.
    # Only the account that successfully pairs is allowed to use the private AI assistant.
    if not is_admin(uid):
        if ADMIN_PAIR_CODE and utterance.strip() == f"관리자등록 {GNJ-Admin-2026-740707}":
            with db() as c:
                c.execute("INSERT OR IGNORE INTO admins(kakao_user_id,created_at) VALUES(?,?)",
                          (uid, datetime.now().isoformat(timespec="seconds")))
            return kakao_text("GNJ 관리자 등록이 완료되었습니다. 이제 대표님 전용 AI 영업비서를 사용할 수 있습니다.")
        return kakao_text("안녕하세요. 지앤제이시스템 상담 채널입니다.\n제품·렌탈·납품 문의는 문의 내용을 남겨주시면 안내해 드리겠습니다.")

    if not utterance:
        return kakao_text("질문이나 영업 업무를 입력해 주세요.")

    if utterance in ("도움말", "사용법", "/help"):
        return kakao_text(
            "GNJ AI 영업비서 사용법\n"
            "· 자연어로 영업 전략과 분석 요청\n"
            "· 영업처등록 기관명 | 상담내용 | 다음 행동\n"
            "· 영업처목록\n"
            "· 대화초기화\n\n"
            "주의: 현재 초기 버전에는 실시간 웹 검색, 메일 발송, 자동 알림이 아직 연결되지 않았습니다."
        )

    if utterance.startswith("영업처등록 "):
        return kakao_text(save_lead(utterance[len("영업처등록 "):]))

    if utterance in ("영업처목록", "저장한 영업처"):
        return kakao_text(list_leads())

    if utterance == "대화초기화":
        with db() as c:
            c.execute("DELETE FROM history WHERE kakao_user_id=?", (uid,))
        return kakao_text("대화 문맥을 초기화했습니다. 영업처 저장 내용은 유지됩니다.")

    if client is None:
        return kakao_text("AI API 키가 서버에 설정되지 않았습니다. 관리자에게 문의해 주세요.")

    try:
        history = get_history(uid)
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=history + [{"role": "user", "content": utterance}],
        )
        answer = response.output_text.strip() or "답변을 생성하지 못했습니다. 다시 질문해 주세요."
        remember(uid, "user", utterance)
        remember(uid, "assistant", answer)
        return kakao_text(answer)
    except Exception as exc:
        log.exception("OpenAI request failed")
        return kakao_text(f"AI 연결 중 오류가 발생했습니다. 관리자에게 문의해 주세요. ({type(exc).__name__})")

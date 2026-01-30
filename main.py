import asyncio
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
import re

from agent import process_message, get_agent

# .env 불러오기
load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

# 전역 event loop
_loop = None
_loop_thread = None


def get_or_create_loop():
    """전역 event loop 가져오기 또는 생성"""
    global _loop, _loop_thread
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        _loop_thread = threading.Thread(target=_loop.run_forever, daemon=True)
        _loop_thread.start()
    return _loop


def run_async(coro):
    """비동기 함수를 전역 loop에서 실행"""
    loop = get_or_create_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=300)


# Slack Bolt 앱 초기화
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)


def remove_mention(text: str) -> str:
    """멘션 태그 제거"""
    return re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()


@app.event("app_mention")
def handle_mention(body, say, logger):
    """@멘션 이벤트 처리"""
    event = body["event"]
    user = event["user"]
    text = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])

    logger.info(f"받은 메시지: {text}")

    # 멘션 제거 후 실제 메시지 추출
    user_message = remove_mention(text)

    if not user_message:
        say(
            text=f"<@{user}> 무엇을 도와드릴까요? GitHub PR, Jira 티켓 등을 조회할 수 있어요!",
            thread_ts=thread_ts
        )
        return

    # 진행 상황 콜백 함수
    async def progress_callback(message: str):
        """진행 상황을 Slack으로 전송"""
        loop = get_or_create_loop()
        # 동기 함수 say를 비동기에서 호출
        await loop.run_in_executor(None, lambda: say(text=message, thread_ts=thread_ts))

    # 처리 중 메시지
    say(text="처리 시작... :hourglass_flowing_sand:", thread_ts=thread_ts)

    try:
        response = run_async(process_message(user_message, progress_callback))
        say(text=response, thread_ts=thread_ts)

    except Exception as e:
        logger.error(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()
        say(
            text=f"<@{user}> 처리 중 오류가 발생했어요: {str(e)}",
            thread_ts=thread_ts
        )


@app.event("app_home_opened")
def handle_app_home(event, client, logger):
    """앱 홈 오픈 이벤트"""
    logger.info("App Home opened")


if __name__ == "__main__":
    print("=== 히스토리 에이전트 시작 ===")

    # 전역 event loop 및 에이전트 초기화
    get_or_create_loop()
    run_async(get_agent())

    print("Slack 연결 중...")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

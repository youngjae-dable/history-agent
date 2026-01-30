import os
import subprocess
from dotenv import load_dotenv

load_dotenv()


def load_system_prompt() -> str:
    """prompt.md 파일에서 시스템 프롬프트 로드"""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "당신은 개발팀을 돕는 히스토리 에이전트입니다."


class HistoryAgent:
    def __init__(self):
        pass  # MCP 설정은 ~/.claude.json의 프로젝트별 설정 사용

    async def setup(self):
        """에이전트 초기화"""
        print("에이전트 초기화 완료")

    async def chat(self, user_message: str, progress_callback=None) -> str:
        """사용자 메시지 처리 및 응답 생성"""
        try:
            if progress_callback:
                await progress_callback("🔍 검색 중...")

            # claude CLI 경로 찾기
            claude_path = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True
            ).stdout.strip() or "claude"

            # claude CLI 명령어 구성 (print mode: -p)
            cmd = [
                claude_path,
                "-p",  # print mode (stdin에서 프롬프트 읽기)
                # 프로젝트 MCP 설정 사용 (~/.claude.json의 프로젝트별 설정)
                "--dangerously-skip-permissions"
            ]

            # 프롬프트 구성
            system_prompt = load_system_prompt()
            full_prompt = system_prompt + "\n\n사용자 메시지: " + user_message

            # claude CLI 호출 (프로젝트 경로에서 실행하여 프로젝트 MCP 설정 사용)
            project_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                cwd=project_dir,  # 프로젝트 경로에서 실행
                env=os.environ.copy()  # 기존 환경 변수 유지
            )

            # stdout이 있으면 반환
            if result.stdout and result.stdout.strip():
                return result.stdout.strip()

            # stderr가 있으면 에러 반환
            if result.stderr and result.stderr.strip():
                return f"오류: {result.stderr.strip()}"

            return "검색 결과를 찾을 수 없습니다."

        except subprocess.TimeoutExpired:
            return "요청 시간이 초과되었습니다. (5분)"
        except FileNotFoundError:
            return "Claude CLI를 찾을 수 없습니다. 'npm install -g @anthropic-ai/claude'로 설치해주세요."
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"오류 발생: {str(e)}"


# 전역 에이전트 인스턴스
_agent = None


async def get_agent() -> HistoryAgent:
    """에이전트 인스턴스 가져오기 (싱글톤)"""
    global _agent
    if _agent is None:
        _agent = HistoryAgent()
        await _agent.setup()
    return _agent


async def process_message(message: str, progress_callback=None) -> str:
    """메시지 처리 진입점"""
    ag = await get_agent()
    return await ag.chat(message, progress_callback)

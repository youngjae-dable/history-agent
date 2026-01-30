# History Agent

개발팀을 위한 Slack 기반 히스토리 검색 에이전트입니다. Jira 티켓과 GitHub PR을 자연어로 검색할 수 있습니다.

> **참고**: 현재 dable 팀용 Slack 앱이 내장되어 있습니다. 다른 팀에서 사용하려면 Slack 앱을 새로 생성해야 합니다. Slack 토큰은 별도 문서를 참고하세요.

## 기능

- Jira 티켓 검색 (Atlassian 공식 Rovo MCP Server)
- GitHub PR/Issue 검색
- 자연어 기반 검색
- Slack에서 멘션으로 사용

## 설치

### 1. 사전 요구사항

```bash
# Python 3.9+
pip3 install slack-bolt python-dotenv

# Claude Code CLI
npm install -g @anthropic-ai/claude
```

### 2. 레포지토리 복제

```bash
git clone https://github.com/your-username/history-agent.git
cd history-agent
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일에서 `GITHUB_TOKEN`을 본인의 토큰으로 교체하세요:
```
GITHUB_TOKEN=ghp_your_github_token_here
```

GitHub 토큰 생성: https://github.com/settings/tokens

### 4. MCP 서버 설정 (선택 - Jira 사용 시)

```bash
# Atlassian Rovo MCP Server 추가
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp

# OAuth 인증
claude
# /mcp 입력 → atlassian 선택 → Authenticate 클릭
```

### 5. 실행

```bash
python main.py
```

Slack에서 `@history-agent`를 멘션하여 사용하세요.

## 사용 예

```
@history-agent ML 프로젝트의 진행 중인 이슈 보여줘
@history-agent 학습 기간 관련 PR 검색해줘
@history-agent ML-4900 티켓 요약해줘
```

## 기본 설정

- 기본 Jira 프로젝트: `Machine Learning`
- 기본 GitHub 레포지토리: `teamdable/ai-craft`

## 프로젝트 구조

```
history-agent/
├── main.py           # Slack 앱 진입점
├── agent.py          # Claude 에이전트 래퍼
├── prompt.md         # 시스템 프롬프트
├── .env.example      # 환경 변수 템플릿
└── .mcp.json         # MCP 서버 설정 (자동 생성됨)
```

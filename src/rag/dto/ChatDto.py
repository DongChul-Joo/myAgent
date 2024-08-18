from typing import Optional

from pydantic import Field

class ChatRequestDto:
    message: Optional[str] = Field(None, title="사용자 메세지", description="LLM에 송신할 사용자 채팅 메시지")
from pathlib import Path

import httpx

from core.config import settings
from core.enums import ChatGPTModelsEnum
from core.exceptions import ChatgptException
from core.logger_config import setup_logger

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class ChatGPT:
    def __init__(self, model: ChatGPTModelsEnum,
                 prompt: str):
        self.model = model
        self.prompt = prompt
        self.headers = {
            'Authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }

    async def get_response_text(self, message: str):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=10.0, read=30.0)) as client:
                response = await client.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": f'{self.prompt} {message}'}],
                })
                response_json = response.json()
                return response_json['choices'][0]['message']['content'].strip()
        except Exception as e:
            detail = (f'chatgpt error: ({self.model=}, {message=}): {e.__class__.__name__}: {str(e)}')
            logger.error(detail)
            raise ChatgptException(detail)

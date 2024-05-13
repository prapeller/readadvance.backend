import httpx

from core.config import settings
from core.enums import ChatGPTModelsEnum


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
        async with httpx.AsyncClient() as client:
            response = await client.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json={
                "model": self.model,
                "messages": [{"role": "user", "content": f'{self.prompt} {message}'}],
            })
            response_json = response.json()
            return response_json['choices'][0]['message']['content'].strip()

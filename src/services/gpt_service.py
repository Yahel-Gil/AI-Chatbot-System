from openai import OpenAI
from utils.app_config import AppConfig

class GptService:

    # OpenAI configuration:
    def __init__(self) -> None:
        self.openai = OpenAI(api_key=AppConfig.chat_gpt_api_key)

    # Get GPT completion:
    def get_completion(self, messages: list) -> str:

        # Data to send:
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # Return completion:
        completion = response.choices[0].message.content
        return completion # type: ignore

# Export a single instance of the service:
gpt_service = GptService()
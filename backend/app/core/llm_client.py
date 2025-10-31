import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.language_models import BaseLLM
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import Generation,LLMResult
from pydantic import Field
from app.core.buffer_manager import MemoryManager
from typing import List, Optional
import requests

load_dotenv()

class GithubLLM(BaseLLM):
    api_key: str = Field(..., description="API key for GitHub Models or OpenAI")
    model: str = Field(default="gpt-4.1", description="Model name to use")
    base_url: str = Field(default="https://models.github.ai/inference", description="Custom API base endpoint")

    client: Optional[OpenAI] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, run_manager = Optional[CallbackManagerForLLMRun], **kwargs) -> LLMResult:
        generations = []
        try:
            print("We are here!!")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise, helpful assistant."},
                    {"role": "user", "content": prompts[0]},
                ],
                temperature=0.7,
                top_p=1.0,
            )

            text = response.choices[0].message.content
            generations.append([Generation(text=text)])
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            generations.append([Generation(text=f"Error generating response: {str(e)}")])

        return LLMResult(generations=generations)
    
    @property
    def _llm_type(self) -> str:
        return "github-models"
    
class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("MODEL_NAME")
        base_url = os.getenv("BASE_URL")
        
        self.memory = MemoryManager(max_messages=10)
        self.langchain_memory = ConversationBufferMemory(return_messages = True)
        self.llm = GithubLLM(api_key=api_key,model=model,base_url=base_url)
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.langchain_memory,
            verbose=False            
        )
        
    async def get_reply(self, user_message: str) -> str:
        self.memory.add("user", user_message)
        reply = self.chain.run(user_message)
        self.memory.add("assistant", reply)
        return reply
        
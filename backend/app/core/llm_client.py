import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.language_models import BaseLLM
from langchain_classic.chains.conversation.base import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from app.core.buffer_manager import MemoryManager
from typing import List, Optional

load_dotenv()

class GithubLLM(BaseLLM):
    def __init__(self, api_key: str, model:str, base_url:str):
        super().__init__()
        self.client = OpenAI(
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        self.model = model
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a concise, helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            top_p=1.0,
        )
        return response[0].message.content
    
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
        self.llm = GithubLLM(api_key,model,base_url)
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
        
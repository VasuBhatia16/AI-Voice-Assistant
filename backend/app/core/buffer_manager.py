from collections import deque
from typing import List, Dict
import json

try:
    from app.core.redis_client import redis_client
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

class MemoryManager:
    def __init__(self,session_id: str, max_messages: int = 10):
        self.buffer = deque(maxlen=max_messages)
        self.session_id = session_id
        
    def add(self, role: str, content: str):
        self.buffer.append({"role":role, "content":content})
        
    def history(self,buffer: List[Dict[str,str]]):
        return list(self.buffer)
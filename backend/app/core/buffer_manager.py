from collections import deque
from typing import List, Dict


class MemoryManager:
    def __init__(self, max_messages: int = 10):
        self.buffer = deque(maxlen=max_messages)
    def add(self, role: str, content: str):
        self.buffer.append({"role":role, "content":content})
    def history(self,buffer: List[Dict[str,str]]):
        return list(self.buffer)
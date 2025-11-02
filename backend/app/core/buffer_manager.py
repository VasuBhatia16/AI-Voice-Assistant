from collections import deque
from typing import List, Dict
import json
import time
import redis

TTL_SECONDS = 3600
try:
    from app.core.redis_client import redis_client
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


def _get_key(session_id: str) -> str:
    return f"chat_history:{session_id}"

class MemoryManager:
    
    def __init__(self,session_id: str, max_messages: int = 10):
        self.buffer = deque(maxlen=max_messages)
        self.session_id = session_id
        
    def add(self, role: str, content: str):
        message = {"role": role, "content": content, "ts": int(time.time())}
        self.buffer.append({"role":role, "content":content})
        
        if REDIS_AVAILABLE and self.session_id:
            key =  _get_key(self.session_id)
            redis_client.rpush(key, json.dumps(message))
            redis_client.expire(key, TTL_SECONDS)
        
    def load_history(self) ->  List[Dict[str,str]]:
        if REDIS_AVAILABLE and self.session_id:
            key = _get_key(self.session_id)
            items = redis_client.lrange(key,0,-1)
            parsed = []
            for item in items:
                try:
                    parsed.append(json.loads(item))
                except Exception as e:
                    try:
                        parsed.append(json.loads(item.decode("utf-8")))
                    except Exception:
                        print(f"Couldn't parse: {str(e)}")
            self.buffer.clear()
            for msg in parsed[-self.buffer.maxlen:]:
                self.buffer.append(msg)
            return parsed
        return list(self.buffer)
                
    def history(self):
        return self.load_history()
    
    def clear_session(self):
        self.buffer.clear()
        if REDIS_AVAILABLE and self.session_id:
            redis_client.delete(_get_key(self.session_id))
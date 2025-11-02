from pydantic import BaseModel

class VoiceInput(BaseModel):
    audio_base64: str
class VoiceResponse(BaseModel):
    text: str
    audio_base64: str
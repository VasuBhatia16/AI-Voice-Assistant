import base64
from io import BytesIO
import os
import edge_tts
import speech_recognition as sr
from gtts import gTTS
from fastapi import APIRouter, HTTPException
from pydub import AudioSegment
import logging
from app.models.voice import VoiceInput, VoiceResponse
from app.core.llm_client import LLMClient
import pyttsx3
logger = logging.getLogger(__name__)

llm_client = LLMClient()

router = APIRouter()


def transcribe_audio(audio_buffer: BytesIO) -> str:
    """
    Converts audio buffer to text using Speech Recognition.
    Uses multiple recognition engines as fallback for better reliability.
    
    Flow:
    1. Try Google Web Speech API (free, no API key needed)
    2. Fallback to other engines if available
    3. Return error message if all fail
    
    Args:
        audio_buffer: BytesIO buffer containing WAV audio data
        
    Returns:
        str: Transcribed text or error message
    """
    recognizer = sr.Recognizer()
    user_text = ""
    
    try:
        with sr.AudioFile(audio_buffer) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            try:
                user_text = recognizer.recognize_google(audio_data)
                logger.info("Successfully transcribed using Google Speech API")
            except sr.UnknownValueError:
                logger.warning("Google Speech API could not understand audio")
                try:
                    user_text = recognizer.recognize_sphinx(audio_data)
                    logger.info("Successfully transcribed using Sphinx")
                except:
                    user_text = "Sorry, I could not understand the audio. Please speak more clearly."
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                user_text = "Speech recognition service is currently unavailable. Please try again."
                
    except Exception as e:
        logger.error(f"Error during speech recognition: {type(e).__name__}: {e}")
        user_text = f"Error processing audio: {type(e).__name__}"
    
    return user_text


async def text_to_speech(text: str) -> str:
    """
    Converts text to speech audio using gTTS (Google Text-to-Speech).
    
    Args:
        text: Text to convert to speech
        
    Returns:
        str: Base64-encoded MP3 audio data
    """
    # try:
    #     tts = gTTS(text=text, lang='en', slow=False)
    #     mp3_buffer = BytesIO()
    #     tts.write_to_fp(mp3_buffer)
    #     mp3_buffer.seek(0)
    #     audio_base64 = base64.b64encode(mp3_buffer.read()).decode('utf-8')
    #     return audio_base64
    # except Exception as e:
    #     logger.error(f"Error in text-to-speech conversion: {type(e).__name__}: {e}")
    #     return "" 
    try:
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return audio_base64
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {type(e).__name__}: {e}")
        return ""


@router.post("/process", response_model=VoiceResponse)
async def process_voice(input_data: VoiceInput):
    """
    Main endpoint for processing voice input from the user.
    
    Processing Pipeline:
    1. Decode base64 audio → Convert to WAV format
    2. Speech-to-Text (STT) → Extract user's message
    3. LLM Processing → Generate AI response (with conversation memory)
    4. Text-to-Speech (TTS) → Convert response to audio
    5. Return both text and audio response
    
    Args:
        input_data: VoiceInput containing base64-encoded audio data
        
    Returns:
        VoiceResponse: Contains assistant's text response and base64-encoded audio
        
    The audio input format can be various (webm, mp3, wav, etc.) and will be
    automatically converted to WAV for speech recognition.
    """
    
    try:
        audio_bytes = base64.b64decode(input_data.audio_base64)
        audio_buffer = BytesIO(audio_bytes)
        
        sound = None
        formats_to_try = ["wav", "mp3", "webm", "ogg", "flac", "m4a"]
        
        for fmt in formats_to_try:
            try:
                audio_buffer.seek(0)
                sound = AudioSegment.from_file(audio_buffer, format=fmt)
                logger.info(f"Successfully loaded audio as {fmt} format")
                break
            except:
                continue
    
        if sound is None:
            try:
                audio_buffer.seek(0)
                sound = AudioSegment.from_file(audio_buffer)
                logger.info("Successfully loaded audio with auto-detection")
            except Exception as auto_error:
                logger.error(f"Failed to load audio with auto-detection: {auto_error}")
                raise ValueError(f"Unsupported audio format. Tried: {', '.join(formats_to_try)}")
        
        try:
            sound = sound.normalize()
        except:
            logger.warning("Audio normalization failed, continuing without it")
        
        wav_buffer = BytesIO()
        try:
            sound.export(wav_buffer, format="wav", parameters=["-ar", "16000"])
        except:
            sound.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        logger.info(f"Successfully decoded audio: {len(audio_bytes)} bytes, duration: {len(sound)}ms")
        
    except Exception as e:
        logger.error(f"Error decoding audio: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format or corrupted audio data: {type(e).__name__}: {str(e)}"
        )
    
    user_text = transcribe_audio(wav_buffer)
    
    if user_text.startswith("Sorry") or user_text.startswith("Speech") or user_text.startswith("Error"):
        return VoiceResponse(
            text=user_text,
            audio_base64=""
        )
    
    logger.info(f"Transcribed user input: {user_text[:50]}...")
    
    try:
        session_id = getattr(input_data, "session_id", None)
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        assistant_response = await llm_client.get_reply(user_message=user_text,session_id=session_id)
        logger.info(f"Generated LLM response: {assistant_response[:50]}...")
    except Exception as e:
        logger.error(f"Error in LLM processing: {type(e).__name__}: {e}")
        assistant_response = f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {type(e).__name__}"
    
    output_audio_base64 = await text_to_speech(assistant_response)
    
    if not output_audio_base64:
        logger.warning("TTS failed, returning text-only response")
    if output_audio_base64:
        try:
            with open("response.mp3", "wb") as f:
                f.write(base64.b64decode(output_audio_base64))
        except Exception as e:
            logger.error(f"Failed to save response.mp3: {e}")
    return VoiceResponse(
        text=assistant_response,
        audio_base64=output_audio_base64
    )



def speech_to_text(audio_file):
    try:
        print(f"📂 Reading audio file: {audio_file}")
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
    
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        print("Error")
from groq import Groq
import os

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

LANGUAGE_MAP = {
    'english': 'en',
    'malay': 'ms',
    'chinese': 'zh',
    'mandarin': 'zh',
}

def transcribe_audio(file_path: str) -> dict:
    with open(file_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model='whisper-large-v3',
            file=f,
            response_format='verbose_json'
        )
    raw = (response.language or 'english').lower()
    return {
        'text': response.text,
        'language': LANGUAGE_MAP.get(raw, 'en'),
        'raw_language': raw
    }
import configparser

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from openai import OpenAI




class Audio(BaseModel):
    filePath: str


def read_api_key(config_file='config.ini', section='API', key):
    config = configparser.ConfigParser()
    config.read(config_file)

    if section in config and key in config[section]:
        return config[section][key]
    else:
        raise KeyError(f"'{key}' not found in section '{section}' of the config file.")


def transcribe_audio(audio: Audio):
    audio_fp = audio.filePath
    audio_file = open(audio_fp, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcription)
    print(transcription.text)
    return transcription.text


app = FastAPI()
router = APIRouter()
client = OpenAI(api_key=read_api_key(key='openai'))
@router.post("/transcribe/")
def create_item(audio: Audio):
    trascribed_text = transcribe_audio(audio)
    return {"message": trascribed_text}

app.include_router(router)
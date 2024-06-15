import configparser
import glob
import os

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from openai import OpenAI
import shutil


class Audio(BaseModel):
    filePath: str


def read_api_key(key, config_file='config.ini', section='API'):
    config = configparser.ConfigParser()
    config.read(config_file)

    if section in config and key in config[section]:
        return config[section][key]
    else:
        raise KeyError(f"'{key}' not found in section '{section}' of the config file.")


def transcribe_audio(audio: Audio):
    print(audio.filePath)
    audio_fp = audio.filePath
    audio_file = open(audio_fp, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(transcription)
    print(transcription.text)
    return transcription.text


def translate_audio(audio: Audio):
    print(audio.filePath)
    audio_fp = audio.filePath
    audio_file = open(audio_fp, "rb")
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )
    print(translation)
    print(translation.text)
    return translation.text


def summarize_audio(username):
    audio_dir_incoming = os.path.join(data_path, 'audio', 'incoming', username)
    audio_dir_processed = os.path.join(data_path, 'audio', 'processed', username)
    if not os.path.exists(audio_dir_processed):
        os.makedirs(audio_dir_processed)
        print(f"Directory {audio_dir_processed} created successfully.")
    else:
        print(f"Directory {audio_dir_processed} already exists.")

    print(audio_dir_incoming)
    ogg_files = glob.glob(os.path.join(audio_dir_incoming, '*.ogg'))
    conversation = ''
    for ogg_file in ogg_files:
        conversation = conversation + ' ' + translate_audio(ogg_file)
        shutil.move(ogg_file, audio_dir_processed)
    instructions = summarize_instructions(conversation)
    return instructions


def summarize_instructions(conversation):
    system_prompt = "You are a helpful assistant that can ignore errors in transcription, summarize the messages and capture only the important instructions that are related to popiah stall operations."
    temperature = 0
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Please summarize the following: {conversation}".format(conversation=conversation)
            }
        ]
    )
    print(response)
    return response.choices[0].message.content


app = FastAPI()
router = APIRouter()
client = OpenAI(api_key=read_api_key(key='openai'))
data_path = read_api_key(key='data_path')


@router.post("/transcribe/")
def create_item(audio: Audio):
    trascribed_text = transcribe_audio(audio)
    return {"message": trascribed_text}


@router.post("/translate/")
def create_item(audio: Audio):
    trascribed_text = translate_audio(audio)
    return {"message": trascribed_text}


@router.post("/summarize/")
def summarize_audio(in_parms):
    username = in_parms.username
    in_type = in_parms.type
    if in_type == 'audio':
        instructions = summarize_audio(username)
    return {"message": instructions}


app.include_router(router)

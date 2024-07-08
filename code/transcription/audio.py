import openai
import moviepy.editor as mp
from werkzeug.utils import secure_filename

# Transcribir el audio mediante Whisper (OpenAI):
def transcribe_audio(audio):
    file = open(audio, 'rb')
    transcription = openai.Audio.transcribe("whisper-1", file)
    return transcription["text"]

# Transcribir el audio de un vídeo:
def transcribe_video(video):
    clip = mp.VideoFileClip(video)
    clip.audio.write_audiofile("audio.wav")
    transcription = transcribe_audio("audio.wav")
    return transcription
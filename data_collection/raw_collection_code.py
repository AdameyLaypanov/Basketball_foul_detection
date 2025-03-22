# !pip install pytubefix -q
# !pip install yt_dlp ffmpeg-python torch whisper requests nest_asyncio -q
# !pip install yt-dlp ffmpeg-python pydub requests nest_asyncio -q

# -------------------------------------------------------------------------

# Библиотеки
import os
import sys
import json
import math
import time
import re
import ffmpeg
import requests
import yt_dlp
from pydub import AudioSegment
from IPython.display import clear_output
import nest_asyncio
from pathlib import Path
from typing import List, Dict

nest_asyncio.apply()

# -------------------------------------------------------------------------

# Монтирование Google Drive
from google.colab import drive
drive.mount('/content/drive', force_remount=True)

# -------------------------------------------------------------------------

# Конфигурация Deep Infra
DEEPINFRA_API_KEY = "9kScTQSpFJCd6OdxblR8bHjw3iWSPZkV"
WHISPER_API_URL = "https://api.deepinfra.com/v1/inference/openai/whisper-large"
LLM_API_URL = "https://api.deepinfra.com/v1/inference/meta-llama/Meta-Llama-3-70B-Instruct"

# Путь к cookies файлу 
COOKIES_PATH = "/content/drive/MyDrive/ds_one/cookies.txt"
VIDEO_URL = "https://youtu.be/ufOiMggc6pw?si=Hj0LN_Rwknk29OOw"
# -------------------------------------------------------------------------
class Config:
    DRIVE_PATH = "/content/drive/MyDrive/ds_one"    # Папка на Google Drive для результатов
    TEMP_DIR = "/content/temp"                      # Временная папка
    FRAME_RATE = 18                                 # Сколько кадров/сек при сохранении
    MAX_AUDIO_SIZE_MB = 5                           # Размер одного чанка (уменьшаем для долгих видео)
    AUDIO_BITRATE = '128k'
    SAMPLE_RATE = 16000
    TRANSCRIBE_RETRIES = 2                          # Повторные попытки при таймауте
    TRANSCRIBE_TIMEOUT = 120                        # Секунд ожидания ответа Whisper

    @classmethod
    def setup(cls):
        os.makedirs(cls.DRIVE_PATH, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)

Config.setup()
# -------------------------------------------------------------------------
def convert_to_mp3(input_path: str) -> str:
    """Конвертация аудио из WAV в MP3"""
    output_path = Path(input_path).with_suffix(".mp3")
    (
        ffmpeg
        .input(input_path)
        .output(
            str(output_path),
            acodec='libmp3lame',
            audio_bitrate=Config.AUDIO_BITRATE,
            ar=str(Config.SAMPLE_RATE)
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return str(output_path)
# -------------------------------------------------------------------------
def split_audio(input_path: str) -> List[str]:
    """
    Разделение аудио на чанки по MAX_AUDIO_SIZE_MB,
    чтобы снизить риск таймаута при больших файлах
    """
    chunk_size = Config.MAX_AUDIO_SIZE_MB * 1024 * 1024
    file_size = os.path.getsize(input_path)

    if file_size <= chunk_size:
        return [input_path]

    audio = AudioSegment.from_file(input_path)
    duration_ms = len(audio)
    chunk_duration_ms = int((chunk_size / file_size) * duration_ms)

    chunks = []
    for i in range(0, math.ceil(duration_ms / chunk_duration_ms)):
        start = i * chunk_duration_ms
        end = min((i+1) * chunk_duration_ms, duration_ms)
        chunk = audio[start:end]
        chunk_path = Path(input_path).with_name(f"{Path(input_path).stem}_part{i}.mp3")
        chunk.export(chunk_path, format="mp3", bitrate=Config.AUDIO_BITRATE)
        chunks.append(str(chunk_path))

    return chunks
# -------------------------------------------------------------------------
def transcribe_chunk(chunk_path: str) -> str:
    """Отправка одного аудио-фрагмента на DeepInfra Whisper"""
    headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}
    for attempt in range(Config.TRANSCRIBE_RETRIES):
        try:
            with open(chunk_path, "rb") as f:
                response = requests.post(
                    WHISPER_API_URL,
                    headers=headers,
                    files={"audio": f},
                    timeout=Config.TRANSCRIBE_TIMEOUT
                )
            if response.status_code == 200:
                # Успешно
                return response.json().get("text", "")
            else:
                print(f"Ошибка транскрибации (статус {response.status_code}): {response.text}")
                return ""
        except requests.exceptions.ReadTimeout:
            print(f"⏱ Таймаут при транскрибации {Path(chunk_path).name}. Повтор {attempt+1}/{Config.TRANSCRIBE_RETRIES}")
            if attempt < Config.TRANSCRIBE_RETRIES - 1:
                time.sleep(5)
                continue
            else:
                print("❌ Превышено количество попыток.")
                return ""
        except Exception as e:
            print(f"❌ Ошибка при транскрибации {Path(chunk_path).name}: {e}")
            return ""
    return ""
# -------------------------------------------------------------------------
def transcribe_audio(audio_path: str) -> str:
    """
    Основная транскрибация:
      1. WAV -> MP3
      2. Разбивка на чанки
      3. Отправка каждого чанка на Whisper
    """
    mp3_path = convert_to_mp3(audio_path)
    chunks = split_audio(mp3_path)
    full_text_list = []
    for i, chunk_path in enumerate(chunks, 1):
        print(f"🔊 Транскрибируем фрагмент {i}/{len(chunks)}: {Path(chunk_path).name}")
        text = transcribe_chunk(chunk_path)
        full_text_list.append(text)
        os.remove(chunk_path)
    return " ".join(full_text_list)
# -------------------------------------------------------------------------
def extract_json_array(text: str) -> List[Dict]:
    """
    Удаляем код-блоки (```...```),
    ищем JSON-массив между первой '[' и последней ']'.
    """
    text_no_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    start_idx = text_no_code.find('[')
    end_idx = text_no_code.rfind(']')
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        raise ValueError("Не найден валидный JSON-массив в ответе LLM.")
    array_str = text_no_code[start_idx:end_idx+1].strip()
    return json.loads(array_str)

def process_transcription(full_text: str) -> List[Dict]:
    """
    Анализ текста через LLM -> JSON с key= [start_time, end_time, text]
    """
    prompt = f"""
You are a sports analysis assistant. Analyze the following transcript of a basketball match and extract only the moments when a foul occurred.
Return a valid JSON array of objects. Each object must have exactly these keys:
  "start_time": a number representing the start time in seconds,
  "end_time": a number representing the end time in seconds,
  "text": a string describing the foul.
Do not include any additional text, commentary, or markdown formatting. Your entire answer must be a valid JSON array.

Transcript:
{full_text}
"""
    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "input": prompt,
        "temperature": 0.3,
        "max_tokens": 2000
    }
    response = requests.post(LLM_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Ошибка LLM: {response.status_code}")
        print(response.text)
        return []
    try:
        data = response.json()
        print("LLM API response:", data)
        if "results" in data and isinstance(data["results"], list) and len(data["results"]) > 0:
            result = data["results"][0].get("generated_text", "")
        elif "choices" in data:
            result = data["choices"][0]["message"]["content"]
        elif "result" in data:
            result = data["result"]
        elif "output" in data:
            result = data["output"]
        else:
            raise KeyError("Нет ключа 'results', 'choices', 'result' или 'output' в ответе")
        return extract_json_array(result)
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return []
# -------------------------------------------------------------------------
def download_video(url: str) -> str:
    """Скачивание видео с YouTube (обязательно с cookies)"""
    print("🔄 Скачиваем видео...")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(Config.TEMP_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    if os.path.exists(COOKIES_PATH):
        ydl_opts['cookies'] = COOKIES_PATH
    else:
        print("⚠ Файл cookies не найден. Нужен cookies.txt для авторизации на YouTube (p.s. нужно расширение в Сhrome)")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        sys.exit(1)
# -------------------------------------------------------------------------
def extract_audio(video_path: str) -> str:
    """Извлечение аудио из видео (wav)"""
    audio_path = Path(video_path).with_suffix('.wav')
    (
        ffmpeg
        .input(video_path)
        .output(str(audio_path), acodec='pcm_s16le', ac=1, ar=Config.SAMPLE_RATE)
        .overwrite_output()
        .run(quiet=True)
    )
    return str(audio_path)
# -------------------------------------------------------------------------
def extract_frames_segment(video_path: str, start: float, end: float, idx: int):
    """
    Для каждого фола: создаём папку "foul_{idx}/frames" и сохраняем
    кадры из исходного видео на интервале [start, end].
    """
    # Создаём папку для данного фола
    foul_dir = Path(Config.DRIVE_PATH) / f"foul_{idx}"
    frames_dir = foul_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    try:
        (
            ffmpeg
            .input(video_path, ss=start, to=end)
            .output(str(frames_dir / "frame_%04d.jpg"), r=Config.FRAME_RATE)
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"✅ Кадры фола #{idx} ({start}-{end}с) сохранены в {frames_dir}")
    except ffmpeg.Error as e:
        print(f"❌ Ошибка извлечения кадров для фола #{idx}: {e.stderr.decode()}")
# -------------------------------------------------------------------------
def process_video(url: str):
    """
    Основной процесс:
      1. Скачиваем и извлекаем аудио
      2. Транскрибируем
      3. LLM -> JSON (список фолов)
      4. Для каждого фола: извлекаем кадры (без сохранения .mp4)
    """
    clear_output()
    print("🚀 Начало обработки...")
    try:
        # 1. Скачиваем видео
        video_path = download_video(url)
        print(f"✅ Видео скачано: {Path(video_path).name}")
        
        # 2. Извлечение аудио
        audio_path = extract_audio(video_path)
        print("✅ Аудио извлечено")
        
        # 3. Транскрибация
        full_text = transcribe_audio(audio_path)
        # Удаляем временный аудио-файл
        os.remove(audio_path)
        print("✅ Транскрибация завершена")
        
        # 4. Анализ текста через LLM 
        fouls = process_transcription(full_text)
        print(f"🎯 Найдено фолов: {len(fouls)}")
        
        # 5. извлекаем кадры из каждого фолового интервала
        for i, foul in enumerate(fouls, start=1):
            start_time = foul.get("start_time", 0)
            end_time   = foul.get("end_time", 0)
            text       = foul.get("text", "")
            
            print(f"\n⚡ Фол #{i}: {start_time}-{end_time} с\n📝 {text}")
            extract_frames_segment(video_path, start_time, end_time, i)
        
        print(f"\n✅ Готово! Кадры сохранены в: {Config.DRIVE_PATH}")
    
    except Exception as e:
        print(f"🔥 Ошибка: {e}")
        sys.exit(1)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    process_video(VIDEO_URL)

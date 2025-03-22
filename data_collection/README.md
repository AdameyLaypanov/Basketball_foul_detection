# DeepInfra NBA Foul Detection & Frame Extraction

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg) 
![FFmpeg](https://img.shields.io/badge/FFmpeg-5.x-green.svg)
![Requests](https://img.shields.io/badge/Requests-2.x-orange.svg)
![yt--dlp](https://img.shields.io/badge/yt_dlp-2023.07-yellow.svg)
![DeepInfra](https://img.shields.io/badge/DeepInfra-API-9cf.svg)
![Colab](https://img.shields.io/badge/Google%20Colab-compatible-brightgreen.svg)

<div align="center">
  <img src="https://raw.githubusercontent.com/github/explore/main/topics/youtube/youtube.png" alt="YouTube" width="70" />
  <img src="https://raw.githubusercontent.com/github/explore/main/topics/ffmpeg/ffmpeg.png" alt="FFmpeg" width="70" />
  <img src="https://raw.githubusercontent.com/github/explore/main/topics/python/python.png" alt="Python" width="70" />
</div>

## Overview

Данный проект позволяет:
1. **Скачать видео** с YouTube (через `yt_dlp` и cookies).
2. **Извлечь аудио** из видео и транскрибировать его с помощью API [DeepInfra Whisper](https://deepinfra.com).
3. **Анализировать** расшифровку с помощью LLM DeepInfra для **поиска моментов фолов** (фрагментов с ключевыми фразами).
4. **Вырезать кадры** из каждого найденного интервала, **сохраняя их в отдельные папки** на Google Drive.

Важно:
- Обновлять `cookies.txt`
- Заменить `DRIVE_PATH`
- Адаптировать `FRAME_RATE` и `MAX_AUDIO_SIZE_MB`

## Основной Пайплайн

1. **Скачивание видео**:
   - Используем `yt_dlp` с поддержкой cookies (для авторизации YouTube).
   - Файл cookies (формата Netscape) загружается в Colab и указывается в `COOKIES_PATH`.

2. **Извлечение аудио**:
   - Применяем `ffmpeg` для конвертации видео → `*.wav`.

3. **Транскрибация**:
   - WAV → MP3 (битрейт и частота дискретизации настраиваются).
   - Разбиваем на чанки (по умолчанию `5` МБ), чтобы избежать таймаутов.
   - Каждый чанк отправляем в DeepInfra Whisper API. После успешной транскрибации — удаляем временный файл.

4. **Анализ текста (LLM)**:
   - Готовый транскрибированный текст отправляется в DeepInfra LLM (Meta-Llama).
   - LLM возвращает **JSON-массив**: `[{ "start_time": <float>, "end_time": <float>, "text": <string> }, ...]`.
   - Время — предполагаемая секунда начала/конца фола.

5. **Извлечение кадров**:
   - Для каждого фола создаётся папка `foul_i`.
   - С помощью `ffmpeg` сохраняются кадры (по умолчанию `18` кадров/сек) из `[start_time, end_time]`.
   - Итого получаем набор `frame_0001.jpg, frame_0002.jpg, ...` в папке `foul_i/frames/`.

## Зависимости

- [Python 3.9+](https://www.python.org/downloads/)
- [Requests](https://requests.readthedocs.io/)
- [ffmpeg](https://ffmpeg.org/) 
- [yt_dlp](https://github.com/yt-dlp/yt-dlp)
- [pydub](https://github.com/jiaaro/pydub)
- [nest_asyncio](https://github.com/erdewit/nest_asyncio)
- [DeepInfra API](https://deepinfra.com)

## Установка:
```
!pip install pytubefix -q
!pip install yt_dlp ffmpeg-python torch whisper requests nest_asyncio -q
!pip install yt-dlp ffmpeg-python pydub requests nest_asyncio -q

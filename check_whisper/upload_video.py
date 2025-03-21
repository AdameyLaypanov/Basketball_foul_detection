from pytubefix import YouTube

def download_video(url):
    # Очистка URL от лишних параметров
    url = url.split('?')[0]  # Убираем все параметры после "?"
    yt = YouTube(url)  # Используем pytubefix для загрузки видео
    audio_stream = yt.streams.filter(only_audio=True).first()  # Получаем поток с аудио
    audio_stream.download(output_path="audio", filename="video_audio.mp4")  # Скачиваем аудио
    return "audio/video_audio.mp4"

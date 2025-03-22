# Считывание видео и разбиение на кадры (из Google Drive)
import cv2
import os

# Путь к видео на Google Drive (используем тот же базовый каталог, что и для тренировочных данных)
video_filename = "ллл.mov"
base_data_dir = '/content/drive/MyDrive/kursach/data_testovaya'
video_path = os.path.join(base_data_dir, video_filename)

# Проверяем наличие файла
if not os.path.exists(video_path):
    raise Exception(f"Видео файл {video_filename} не найден в {base_data_dir}")

print("Видео загружается из:", video_path)

# Чтение видео и извлечение кадров
cap = cv2.VideoCapture(video_path)
video_frames = []
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Преобразуем цвет из BGR (OpenCV) в RGB (если требуется для модели)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    video_frames.append(frame_rgb)
    frame_count += 1

cap.release()
print("Количество извлечённых кадров:", frame_count)

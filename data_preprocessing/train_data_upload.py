from google.colab import drive
import os
from pathlib import Path
import random

# Монтирование Google Drive
drive.mount('/content/drive')

# Задаем базовый путь к данным на Google Drive
base_data_dir = '/content/drive/MyDrive/kursach/data_testovaya'
images_dir = os.path.join(base_data_dir, 'images')
labels_dir = os.path.join(base_data_dir, 'labels')
classes_path = os.path.join(base_data_dir, 'classes.txt')

print("Папка с изображениями:", images_dir)
print("Папка с аннотациями:", labels_dir)
print("Файл классов:", classes_path)

# Читаем список классов из файла classes.txt
with open(classes_path, "r") as f:
    classes = f.read().splitlines()
print("Список классов:", classes)

# Получаем список файлов изображений (поддерживаемые форматы: jpg, jpeg, png)
image_paths = [p for p in Path(images_dir).rglob("*") 
               if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

# Формируем пары: для каждого изображения ищем файл аннотации с тем же именем, но с расширением .txt
pairs = []
for img_path in image_paths:
    expected_label = img_path.stem + ".txt"
    label_path = Path(labels_dir) / expected_label
    if label_path.exists():
        pairs.append((str(img_path), str(label_path)))
    else:
        print(f"Предупреждение: для файла {img_path.name} не найден файл аннотации {expected_label} в {labels_dir}")

print(f"Найдено пар изображений: {len(pairs)}")

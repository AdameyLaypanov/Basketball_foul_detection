import os
import random
import shutil
from tqdm import tqdm  # Импортируем tqdm

# Укажи путь к твоему датасету
dataset_dir = '/datasets/dataset_test'
images_dir = os.path.join(dataset_dir, 'images')
labels_dir = os.path.join(dataset_dir, 'labels')

# Создаем папки для тренировочных и валидационных данных
train_images_dir = os.path.join(dataset_dir, 'train/images')  # Исправлено
train_labels_dir = os.path.join(dataset_dir, 'train/labels')
val_images_dir = os.path.join(dataset_dir, 'val/images')  # Исправлено
val_labels_dir = os.path.join(dataset_dir, 'val/labels')

os.makedirs(train_images_dir, exist_ok=True)
os.makedirs(train_labels_dir, exist_ok=True)
os.makedirs(val_images_dir, exist_ok=True)
os.makedirs(val_labels_dir, exist_ok=True)

# Получаем список всех изображений
images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png'))]

# Разделяем данные: 80% на тренировку и 20% на валидацию
train_images = random.sample(images, int(len(images) * 0.8))
val_images = [img for img in images if img not in train_images]

# Функция для перемещения файлов с проверкой наличия аннотации и с прогрессом
def move_files(file_list, src_dir, dst_dir, annotations_src_dir, annotations_dst_dir):
    for file in tqdm(file_list, desc="Moving files", unit="file"):  # Используем tqdm для прогресса
        image_path = os.path.join(src_dir, file)
        label_file = os.path.splitext(file)[0] + '.txt'
        label_path = os.path.join(annotations_src_dir, label_file)

        # Проверка, существует ли файл аннотации
        if os.path.exists(label_path):
            shutil.move(image_path, os.path.join(dst_dir, file))
            shutil.move(label_path, os.path.join(annotations_dst_dir, label_file))
        else:
            print(f"Warning: Annotation for {file} not found.")

# Перемещаем изображения и аннотации с прогрессом
print("Moving training images and annotations...")
move_files(train_images, images_dir, train_images_dir, labels_dir, train_labels_dir)
print("\nMoving validation images and annotations...")
move_files(val_images, images_dir, val_images_dir, labels_dir, val_labels_dir)
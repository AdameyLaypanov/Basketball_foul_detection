import os
import cv2
import numpy as np
import albumentations as A
from tqdm import tqdm
import random

input_folder = '/Users/admlanno/Desktop/Basketball_foul_detection/Frames/guard_4_view_1'
output_folder = '/Users/admlanno/Desktop/Basketball_foul_detection/Frames/guard_4_view_1'

# os.makedirs(output_folder, exist_ok=True)


augmentations = [
    {"name": "horizontal_flip", "transform": A.HorizontalFlip(p=1.0)},  # Горизонтальное отражение
    {"name": "shear_left", "transform": A.Affine(shear={'x': (-15, -15), 'y': (0, 0)}, p=1.0)},  # Сдвиг влево
    {"name": "shear_right", "transform": A.Affine(shear={'x': (15, 15), 'y': (0, 0)}, p=1.0)},  # Сдвиг вправо
    {"name": "brightness_increase", "transform": A.RandomBrightnessContrast(brightness_limit=(0.2, 0.3), contrast_limit=0, p=1.0)},  # Повышение яркости
    {"name": "brightness_decrease", "transform": A.RandomBrightnessContrast(brightness_limit=(-0.3, -0.2), contrast_limit=0, p=1.0)},  # Понижение яркости
    # {"name": "blur", "transform": A.Blur(blur_limit=(5, 5), p=1.0)},  # Размытие с ядром 5x5
    {"name": "gauss_noise", "transform": A.GaussNoise(var_limit=(10.0, 50.0), p=1.0)},  # Шум
]


augmentation_prob = 0.5


image_files = [f for f in os.listdir(input_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]


for image_file in tqdm(image_files, desc="Augmenting images"):
    if random.random() < augmentation_prob:
        image_path = os.path.join(input_folder, image_file)
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        for aug in augmentations:
            augmented = aug["transform"](image=image)
            augmented_image = augmented['image']
            base_name, ext = os.path.splitext(image_file)
            output_name = f"{aug['name']}_{base_name}{ext}"
            output_path = os.path.join(output_folder, output_name)
            cv2.imwrite(output_path, cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR))

print(f"Аугментированные изображения сохранены в {output_folder}")
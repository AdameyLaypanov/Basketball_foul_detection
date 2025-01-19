from PIL import Image
import os

input_folder = "/Users/admlanno/Desktop/Курсовая/raw_data/Frames/illegal_guarding_1_view2"
output_folder = "/Users/admlanno/Desktop/Курсовая/raw_data/Frames/normalized_guard_view2"


os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with Image.open(input_path) as img:
            resized_img = img.resize((1280, 720), Image.LANCZOS)
            resized_img.save(output_path)

print("Изображения успешно отнормированы!")

# from PIL import Image
# import os
#

# input_folder = "/Users/admlanno/Desktop/Курсовая/raw_data/Frames/illegal_guarding_1_view2"
#

# for filename in os.listdir(input_folder):
#     if filename.endswith((".jpg", ".jpeg", ".png")):
#         input_path = os.path.join(input_folder, filename)
#
#         try:
#             with Image.open(input_path) as img:
#                 width, height = img.size  # Получаем размеры изображения
#                 print(f"Файл: {filename}, Размер: {width}x{height}")
#         except Exception as e:
#             print(f"Не удалось обработать файл {filename}: {e}")
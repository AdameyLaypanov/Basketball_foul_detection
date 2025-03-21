
meow_meow - v1 2025-03-19 2:59pm
==============================

This dataset was exported via roboflow.com on March 19, 2025 at 12:00 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 1061 images.
Foul-no-foul are annotated in YOLOv8 format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 640x640 (Stretch)

The following augmentation was applied to create 6 versions of each source image:
* 50% probability of horizontal flip
* 50% probability of vertical flip
* Randomly crop between 0 and 25 percent of the image
* Random rotation of between -15 and +15 degrees
* Random brigthness adjustment of between -18 and +18 percent
* Salt and pepper noise was applied to 0.1 percent of pixels



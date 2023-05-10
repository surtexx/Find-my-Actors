import os
import json
import random
import shutil
import face_recognition
from PIL import Image, UnidentifiedImageError
import uuid
import sys
import albumentations as alb
import cv2
import tensorflow as tf
import numpy as np

all_labels = {}

CURR_PATH = os.path.join(os.getcwd(), "images")
DEST_PATH = os.path.join(os.getcwd(), "data")
os.mkdir(os.path.join(DEST_PATH, "train_images"))
os.mkdir(os.path.join(DEST_PATH, "validation_images"))
os.mkdir(os.path.join(DEST_PATH, "test_images"))
train_labels = open(os.path.join(DEST_PATH, "train_labels.txt"), "w")
validation_labels = open(os.path.join(DEST_PATH, "validation_labels.txt"), "w")
test_labels = open(os.path.join(DEST_PATH, "test_labels.txt"), "w")

augmentor = alb.Compose([alb.HorizontalFlip(p=0.5),
                         alb.RandomBrightnessContrast(p=0.5),
                         alb.RandomGamma(p=0.5),
                         alb.RGBShift(p=0.5),
                         alb.VerticalFlip(p=0.5)])

for label, directory in enumerate(os.listdir(CURR_PATH)):
    all_labels[label] = directory
    for image in os.listdir(os.path.join(CURR_PATH, directory)):
        where_to_move = random.randint(1, 100)
        try:
            image = face_recognition.load_image_file(os.path.join(CURR_PATH, directory, image))
        except UnidentifiedImageError:
            os.remove(os.path.join(CURR_PATH, directory, image))
            continue
        face_locations = face_recognition.face_locations(image)
        if where_to_move <= 65:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                if bottom - top <= 50:
                    continue
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                img_name = str(uuid.uuid1()) + ".jpg"
                pil_image.save(os.path.join(DEST_PATH, "train_images", img_name))
                train_labels.write(f"{img_name} {label}\n")
        elif where_to_move <= 80:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                if bottom - top <= 50:
                    continue
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                img_name = str(uuid.uuid1()) + ".jpg"
                pil_image.save(os.path.join(DEST_PATH, "validation_images", img_name))
                validation_labels.write(f"{img_name} {label}\n")
        else:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                if bottom - top <= 50:
                    continue
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)

                img_name = str(uuid.uuid1()) + ".jpg"
                pil_image.save(os.path.join(DEST_PATH, "test_images", img_name))
                test_labels.write(f"{img_name} {label}\n")

with open(os.path.join(DEST_PATH, "labels.json"), "w") as f:
    json.dump(all_labels, f)


train_labels = open(os.path.join(DEST_PATH, "train_labels.txt"), "r+")
validation_labels = open(os.path.join(DEST_PATH, "validation_labels.txt"), "r+")
test_labels = open(os.path.join(DEST_PATH, "test_labels.txt"), "r+")
train_label = train_labels.readlines()
validation_label = validation_labels.readlines()
test_label = test_labels.readlines()
for index, file in enumerate([train_label, validation_label, test_label]):
    for line in file:
        if index == 0:
            folder = "train_images"
        elif index == 1:
            folder = "validation_images"
        else:
            folder = "test_images"
        image = cv2.imread(os.path.join(DEST_PATH, folder, line.split()[0]))
        label = line.split()[1]
        for i in range(20):
            augmented_image = augmentor(image=image)
            img_name = str(uuid.uuid1()) + ".jpg"
            cv2.imwrite(os.path.join(DEST_PATH, folder, img_name), augmented_image["image"])
            if folder == 'train_images':
                train_labels.write(f"{img_name} {label}\n")
            elif folder == 'validation_images':
                validation_labels.write(f"{img_name} {label}\n")
            else:
                test_labels.write(f"{img_name} {label}\n")
        # cv2.imshow("image", augmented_image["image"])
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
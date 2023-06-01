import cv2
import os
import json

import face_recognition
import magic
import numpy as np



class FMA:
    def __init__(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("face_recognizer1/face_recognizer1.yml")
        self.recognizer = recognizer
        self.labels = json.load(open("fetch_images/labels.json"))

    def predict(self, file):
        if 'image' in magic.from_file(file, mime=True):
            img = face_recognition.load_image_file(file)
            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            faces = face_recognition.face_locations(img)
            names = []
            for top, right, bottom, left in faces:
                roi_gray = gray_img[top:bottom, left:right]
                color = (255, 0, 0)
                stroke = 2
                cv2.rectangle(img, (left, top), (right, bottom), color, stroke)
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = self.labels[str(self.recognizer.predict(roi_gray)[0])]
                names.append(name)
                color = (5, 5, 5)
                stroke = 2
                cv2.putText(img, name, (left, top+10), font, 1, color, stroke, cv2.LINE_AA)
            return cv2.resize(img, (360, 360)), names
        elif 'video' in magic.from_file(file, mime=True):
            pass    # TODO: video face recognition

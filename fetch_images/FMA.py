import cv2
import os
import json
import magic
import numpy as np


class FMA:
    def __init__(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("face_recognizer1.yml")
        self.recognizer = recognizer
        self.labels = json.load(open("labels.json"))

    def predict(self, file):
        if 'image' in magic.from_file(file, mime=True):
            img = cv2.imread(file)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            id_ = str(self.recognizer.predict(img)[0])
            return self.labels[id_]
        elif 'video' in magic.from_file(file, mime=True):
            pass    # TODO: video face recognition

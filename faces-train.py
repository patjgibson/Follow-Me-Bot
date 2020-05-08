import os
import cv2
import pickle
import numpy as np
from PIL import Image

"""
This script creates an identifier which will be trained to identify exact objects (e.g. a human identify to a face)
To train this, a folder must be created with images of said object (e.g. a Justin Bieber folder with images of
Justin Bieber). Place this folder in a folder which has the same directory as this script. Ensure that in the script
below, an appropriate classifier is used to identify the object.
"""

# Base directory of this script. Must also contain "faces" folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "faces")

# Creates classifier object and a recognizer which will be trained.
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

current_id = 0
label_ids = {}

y_labels = []
x_train = []

# Going through each folder and creating identities for each sub-folder
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpg"):
            path = os.path.join(root,file)
            label = os.path.basename(os.path.dirname(path))
            #label = os.path.basename(root)

            # Adds ID to each image to be trained.
            if not label in label_ids:
                label_ids[label] = current_id
                current_id += 1

            id_ = label_ids[label]

            # Detects object in image
            pil_image = Image.open(path).convert("L") #converts to grayscale
            image_array = np.array(pil_image, "uint8")
            faces = face_cascade.detectMultiScale(image_array, scaleFactor = 1.5, minNeighbors = 5)

            # Adds region of interest to a list.
            for(x,y,w,h) in faces:
                roi = image_array[y:y+h, x:x+w]
                x_train.append(roi)
                y_labels.append(id_)

with open("labels.pickle", 'wb') as f:
    pickle.dump(label_ids, f)

recognizer.train(x_train, np.array(y_labels))
recognizer.save("trainer.yml")

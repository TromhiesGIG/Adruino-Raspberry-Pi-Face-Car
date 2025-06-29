import os
import time
import cv2
import numpy as np
from PIL import Image
from threading import Thread

# ----------- Helper: Get face samples and labels ----------
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []

    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')

        # Example filename: Toyin.101.1.jpg → ID is second part
        try:
            Id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(imageNp)
            Ids.append(Id)
        except:
            print(f"❌ Skipped invalid file: {imagePath}")

    return faces, Ids

# ----------- Optional: Visual Counter (for fun) ------------
def counter_img(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    for i, _ in enumerate(imagePaths, start=1):
        print(f"📸 {i} Images Trained", end="\r")
        time.sleep(0.008)

# ----------- Main Training Function ------------------------
def TrainImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Use proper path for TrainingImage
    training_path = os.path.join(os.path.dirname(__file__), '..', 'TrainingImage')
    training_path = os.path.abspath(training_path)

    faces, Ids = getImagesAndLabels(training_path)

    if not faces:
        print("⚠️ No face images found to train.")
        return

    print("🧠 Training in progress...")

    # Start optional visual thread
    Thread(target=counter_img, args=(training_path,)).start()

    recognizer.train(faces, np.array(Ids))

    # Save the trained model
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'TrainingImageLabel')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'Trainner.yml')
    recognizer.save(model_path)

    print("\n✅ Training complete! Model saved to TrainingImageLabel/Trainner.yml")

# Call the function directly when script runs
if __name__ == "__main__":
    TrainImages()

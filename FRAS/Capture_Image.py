import csv
import cv2
import os
import os.path
import unicodedata

print("🚀 Script is running...")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def takeImages():
    Id = input("Enter Your Id: ")
    name = input("Enter Your Name: ")

    if is_number(Id) and name.isalpha():
        # Initialize webcam
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("❌ Failed to access webcam. Please check camera permissions or device.")
            return

        # Safe path to Haar cascade file
        cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml')
        detector = cv2.CascadeClassifier(cascade_path)

        if detector.empty():
            print("❌ Haar cascade file not found or failed to load.")
            cam.release()
            return

        sampleNum = 0
        os.makedirs("TrainingImage", exist_ok=True)
        print("✅ Camera started. Press 'q' to quit early.")

        while True:
            ret, img = cam.read()
            if not ret:
                print("❌ Failed to read from camera.")
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces) == 0:
             print("🔍 No face detected in this frame.")


            for (x, y, w, h) in faces:
                sampleNum += 1
                cv2.rectangle(img, (x, y), (x + w, y + h), (10, 159, 255), 2)
                filename = f"TrainingImage{os.sep}{name}.{Id}.{sampleNum}.jpg"
                cv2.imwrite(filename, gray[y:y + h, x:x + w])
                print(f"📸 Captured image {sampleNum}")

            cv2.imshow('Face Capture', img)

            # Wait 1ms for key, improves responsiveness
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("❎ User exited early.")
                break
            elif sampleNum >= 100:
                print("✅ 100 face samples captured.")
                break

        cam.release()
        cv2.destroyAllWindows()

        # Log user info
        res = f"✅ Images Saved for ID: {Id} Name: {name}"
        print(res)
        header = ["Id", "Name"]
        row = [Id, name]

        student_csv_path = f"StudentDetails{os.sep}StudentDetails.csv"
        os.makedirs("StudentDetails", exist_ok=True)

        if os.path.isfile(student_csv_path):
            with open(student_csv_path, 'a+', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(row)
        else:
            with open(student_csv_path, 'w', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(header)
                writer.writerow(row)

    else:
        if not is_number(Id):
            print("⚠️ Please enter a numeric ID.")
        if not name.isalpha():
            print("⚠️ Please enter an alphabetical name.")

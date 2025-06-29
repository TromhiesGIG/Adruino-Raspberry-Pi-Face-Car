#!/usr/bin/env python3
import os
import cv2
import numpy as np 
import time
import logging as log
import datetime as dt

# creating the title bar function  
def title_bar():
    os.system('clear')  # for Linux/Raspberry Pi
    
    # title of the program  
    print("\t**********************************************")
    print("\t***** Face Recognition Attendance System *****")
    print("\t*****        Raspberry Pi Version       *****")
    print("\t**********************************************")

# creating the user main menu function  
def mainMenu():
    title_bar()
    print()
    print(10 * "*", "WELCOME MENU", 10 * "*")
    print("[1] Check Camera")
    print("[2] Capture Faces")
    print("[3] Train Images")
    print("[4] Recognize & Attendance")
    print("[5] Quit")
    
    while True:
        try:
            choice = int(input("Enter Choice: "))
            
            if choice == 1:
                checkCamera()
                break
            elif choice == 2:
                CaptureFaces()
                break
            elif choice == 3:
                Trainimages()
                break
            elif choice == 4:
                RecognizeFaces()
                break
            elif choice == 5:
                print("Thank You")
                exit()
            else:
                print("Invalid Choice. Enter 1-5")
                continue
        except ValueError:
            print("Invalid Choice. Enter 1-5\n Try Again")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()

# --------------------------------------------------------- 
# Camera test function
def checkCamera():
    print("Testing camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera not accessible!")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    print("✅ Camera is working! Press 'q' to return to menu")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        cv2.imshow('Camera Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q') or key == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    input("Press Enter to return to main menu...")
    mainMenu()

# --------------------------------------------------------------
# Capture faces function - Using your dataset.py logic
def CaptureFaces():
    print("Starting face capture...")
    
    # Create Dataset folder if it doesn't exist
    if not os.path.exists('Dataset'):
        os.makedirs('Dataset')
        print("Created 'Dataset' folder")
    
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    
    # Check if camera is working
    if not cam.isOpened():
        print("❌ Camera not accessible!")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    # Check if cascade file exists
    if detector.empty():
        print("❌ Haar cascade file not found!")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    # Get user ID
    Id = input('Enter your ID: ')
    name = input('Enter your name: ')
    sampleNum = 0
    
    print("📸 Starting face capture...")
    print("Look at the camera and press 'q' when done or wait for 30 photos")
    
    while True:
        ret, img = cam.read()
        
        if not ret:
            print("Failed to grab frame")
            break
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = detector.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Save the captured face
            cv2.imwrite(f"Dataset/{Id}_{sampleNum}.jpg", gray[y:y+h, x:x+w])
            
            # Increment sample number
            sampleNum += 1
            
            # Show progress
            cv2.putText(img, f"Captured: {sampleNum}/30", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display the frame
        cv2.imshow('Capturing Face Data', img)
        
        # Wait for key press
        key = cv2.waitKey(100) & 0xFF
        if key == ord('q'):
            break
        # Break if sample number is more than 30
        elif sampleNum >= 30:
            break
    
    cam.release()
    cv2.destroyAllWindows()
    
    print(f"✅ Successfully captured {sampleNum} face samples for ID: {Id}")
    
    # Save the name mapping
    names_file = "names.txt"
    with open(names_file, "a") as f:
        f.write(f"{Id},{name}\n")
    
    input("Press Enter to return to main menu...")
    mainMenu()

# -----------------------------------------------------------------
# Train images function
def Trainimages():
    print("Starting training...")
    
    if not os.path.exists('Dataset'):
        print("❌ Dataset folder not found! Please capture faces first.")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    images = []
    labels = []
    
    # Read all images from Dataset folder
    for filename in os.listdir('Dataset'):
        if filename.endswith('.jpg'):
            img_path = os.path.join('Dataset', filename)
            img = cv2.imread(img_path, 0)  # Read as grayscale
            
            if img is not None:
                images.append(img)
                # Extract ID from filename (format: ID_number.jpg)
                label = int(filename.split('_')[0])
                labels.append(label)
    
    if len(images) == 0:
        print("❌ No training images found! Please capture faces first.")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    print(f"Found {len(images)} training images")
    
    # Create and train recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))
    
    # Save the trained model
    if not os.path.exists('TrainingImageLabel'):
        os.makedirs('TrainingImageLabel')
    
    recognizer.save('TrainingImageLabel/Trainner.yml')
    print('✅ Training completed successfully!')
    
    input("Press Enter to return to main menu...")
    mainMenu()

# --------------------------------------------------------------------
# Recognition and attendance function
def RecognizeFaces():
    print("Starting face recognition...")
    
    # Check if trained model exists
    if not os.path.exists('TrainingImageLabel/Trainner.yml'):
        print("❌ No trained model found! Please train images first.")
        input("Press Enter to return to main menu...")
        mainMenu()
        return
    
    # Load name mappings
    names = {}
    if os.path.exists('names.txt'):
        with open('names.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    names[int(parts[0])] = parts[1]
    
    # Load trained model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('TrainingImageLabel/Trainner.yml')
    
    # Load face cascade
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    # Create attendance file
    if not os.path.exists('Attendance'):
        os.makedirs('Attendance')
    
    current_date = dt.datetime.now().strftime("%Y-%m-%d")
    attendance_file = f"Attendance/attendance_{current_date}.csv"
    
    file = open(attendance_file, "a")
    file.write("-------------------------------------------------\n")
    file.write(f"        Date: {dt.datetime.now().strftime('%d-%m-%Y')}\n")
    file.write("-------------------------------------------------\n")
    file.write("Time,ID,Name\n")
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cap = cv2.VideoCapture(0)
    
    # Keep track of recognized faces to prevent spam
    last_recognition_time = {}
    
    print("🎥 Recognition started. Press 'q' or ESC to return to menu")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            id_pred, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            # Check if confidence is good enough
            if confidence < 50:
                current_time = dt.datetime.now()
                student_name = names.get(id_pred, f"ID_{id_pred}")
                confidence_text = f"{round(100 - confidence)}%"
                
                # Only log if this person hasn't been recognized in the last 10 seconds
                if (id_pred not in last_recognition_time or 
                    (current_time - last_recognition_time[id_pred]).seconds >= 10):
                    
                    file.write(f"{current_time.strftime('%H:%M:%S')},{id_pred},{student_name}\n")
                    file.flush()  # Ensure data is written immediately
                    last_recognition_time[id_pred] = current_time
                    print(f"✅ Attendance marked: {student_name} (ID: {id_pred}) at {current_time.strftime('%H:%M:%S')}")
                
                display_name = f"{student_name} - {confidence_text}"
                color = (0, 255, 0)  # Green for recognized
            else:
                display_name = f"Unknown - {round(100 - confidence)}%"
                color = (0, 0, 255)  # Red for unknown

            cv2.putText(frame, display_name, (x + 5, y - 5), font, 0.75, (255, 255, 255), 2)

        cv2.imshow('Face Recognition', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q') or key == ord('Q'):  # ESC or q/Q
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    file.close()
    print(f"🎯 Recognition stopped. Attendance saved to: {attendance_file}")
    
    input("Press Enter to return to main menu...")
    mainMenu()

# ---------------main driver ------------------
if __name__ == "__main__":
    try:
        mainMenu()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your setup and try again.")
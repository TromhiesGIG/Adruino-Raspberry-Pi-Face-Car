import datetime
import os
import time
import cv2
import pandas as pd

def recognize_attendence():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Load trained model
    model_path = os.path.join(os.path.dirname(__file__), '..', 'TrainingImageLabel', 'Trainner.yml')
    recognizer.read(model_path)
    
    # Load Haar cascade correctly
    cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml')
    faceCascade = cv2.CascadeClassifier(cascade_path)
    
    # Load student details
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'StudentDetails', 'StudentDetails.csv')
    df = pd.read_csv(csv_path)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)
    
    # Keep track of already marked attendances to prevent spam
    marked_ids = set()
    
    # Initialize webcam
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Unable to access the webcam. Please check your device or try a different index (e.g., 1 instead of 0).")
        return
    
    cam.set(3, 640)
    cam.set(4, 480)
    
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    
    print("🎥 Starting recognition. Press 'q' to quit.")
    
    while True:
        ret, im = cam.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(int(minW), int(minH)), flags=cv2.CASCADE_SCALE_IMAGE)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (10, 159, 255), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            
            if conf < 100:
                name_arr = df.loc[df['Id'] == Id]['Name'].values
                name = name_arr[0] if len(name_arr) > 0 else "Unknown"
                confstr = "  {0}%".format(round(100 - conf))
                display_name = f"{Id}-{name}"
            else:
                name = "Unknown"
                display_name = name
                confstr = "  {0}%".format(round(100 - conf))
            
            # Only add to attendance if confidence is good AND not already marked
            if (100 - conf) > 50 and Id not in marked_ids:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                attendance.loc[len(attendance)] = [Id, name, date, timeStamp]
                marked_ids.add(Id)  # Add to marked set to prevent duplicates
                display_name += " [Pass]"
                print(f"📝 Attendance marked: ID={Id}, Name={name}, Time={timeStamp}")
                
                # Write to CSV immediately when attendance is marked
                attendance_dir = os.path.join(os.path.dirname(__file__), '..', 'Attendance')
                os.makedirs(attendance_dir, exist_ok=True)
                current_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                filename = f"Attendance_{current_date}.csv"
                filepath = os.path.join(attendance_dir, filename)
                
                # Create new record for just this person
                new_record = pd.DataFrame([[Id, name, date, timeStamp]], columns=col_names)
                
                # Append to existing file or create new one
                if os.path.exists(filepath):
                    new_record.to_csv(filepath, mode='a', header=False, index=False)
                else:
                    new_record.to_csv(filepath, mode='w', header=True, index=False)
                
                print(f"💾 Attendance saved to: {filepath}")
            elif Id in marked_ids:
                display_name += " [Already Marked]"
            
            # Show labels on image
            cv2.putText(im, str(display_name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1,
                       (0, 255, 0) if (100 - conf) > 67 else (0, 255, 255) if (100 - conf) > 50 else (0, 0, 255), 1)
        
        cv2.imshow('Attendance', im)
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    # Now save the attendance data after pressing 'q'
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')
    attendance_dir = os.path.join(os.path.dirname(__file__), '..', 'Attendance')
    os.makedirs(attendance_dir, exist_ok=True)
    filename = f"Attendance_{date}_{timeStamp}.csv"
    filepath = os.path.join(attendance_dir, filename)
    
    if not attendance.empty:
        attendance.to_csv(filepath, index=False)
        print(f"✅ Attendance saved to: {filepath}")
        print(f"📊 Total attendance entries: {len(attendance)}")
    else:
        print("⚠️ No attendance entries to save.")
    
    cam.release()
    cv2.destroyAllWindows()
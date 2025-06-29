import cv2
import time
import os
import numpy as np

def capture_dataset():
    # Create Dataset folder if it doesn't exist
    if not os.path.exists('Dataset'):
        os.makedirs('Dataset')
        print("Created 'Dataset' folder")
    
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    
    # Check if camera is working
    if not cam.isOpened():
        print("❌ Camera not accessible!")
        return False
    
    # Check if cascade file exists
    if detector.empty():
        print("❌ Haar cascade file not found!")
        return False
    
    # Get user ID - Fixed for Python 3
    Id = input('Enter your ID: ')
    sampleNum = 0
    
    print("📸 Starting face capture...")
    print("Look at the camera and press 'q' when done or wait for 30 photos")
    
    while True:
        ret, img = cam.read()
        
        if not ret:
            print("Failed to grab frame")
            break
            
        # Display the frame
        cv2.imshow('Capturing Face Data', img)
        
        # Convert to grayscale - Fixed the color conversion
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
        
        # Show the frame with rectangles
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
    return True

# If running this file directly
if __name__ == "__main__":
    capture_dataset()
# Author: Patrick Gibson
# Date: March 13, 2020
#
# Description: This script tracks and identifies individuals within the frame
#               before forwarding information, such as distance and angle
#               from center of the screen, about the desired userto the
#               Arduino.
#
# Status:   Incomplete due to COVID-19

# Sends string to arduino. Encoded as 8-bit value.

def sendToArduino(sendStr):
    arduino.write(sendStr.encode('utf-8'))

#===========================================================================

# Recevies a message from Arduino. Works by seacrhing for the start marker,
# then recording values until the end marker is found.


def recvFromArduino():
    global startMarker, endMarker

    data = ""
    inputByte = "0"
    byteCount = -1

    while ord(inputByte) != startMarker:
        inputByte = arduino.read()

    while ord(inputByte) != endMarker:
        if ord(inputByte) != startMarker:
            data = data + inputByte.decode("utf-8")
            byteCount += 1
        inputByte = arduino.read()
    
    return(data)

#===========================================================================

# Waits for the arduino to be ready for beginning to send it messages.

def waitForArduino():
    global startMarker, endMarker

    message = ""

    while message.find("Arduino is ready") == -1:
        while arduino.inWaiting() == 0:
            pass
        
        message = recvFromArduino()

        print(message)
        print()

#===========================================================================

# Script begins here

import cv2              # Image Recognition
import serial           # Serial communication through USB
import time             # For delays

# Begins serial communication
serialPort = "COM10"
baudRate = 9600
arduino = serial.Serial(serialPort, baudRate)
print ("Serial port " + serialPort + " opened  Baudrate " + str(baudRate))

startMarker = ord("<")
endMarker = ord(">")
waitForArduino()

# Classifier to identify objects within images
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt2.xml')

# Setting up the camera
cap = cv2.VideoCapture(0)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)

# Values for later
scaleFactor = 1.5
minNeighbors = 5

font = cv2.FONT_HERSHEY_SIMPLEX
text = 'Cutie'

# While the camera is open
while cap.isOpened():
    # Reads frame, converts to gray and looks for faces
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor, minNeighbors)

    waitingForReply = False
    
    # Goes through each face
    for (x,y,w,h) in faces:
        # Encodes centre of face to an 8-bit number
        xPos = str(round((((x+w)/2 - w/2)/(width - w/2) - 0.5) * 100, 1))
        #yPos = str(round((((y+h)/2 - h/2)/(height - h/2) - 0.5) * 100, 1))

        dataToSend = "<" + str(xPos) + "," + str(w) + ">"
        if waitingForReply == False:
            sendToArduino(dataToSend)
            print("Sent from PC: " + dataToSend)
            waitingForReply = True
            
        if waitingForReply == True:
            while arduino.inWaiting() == 0:
                pass

            dataRecvd = recvFromArduino()
            print("Reply received: " + dataRecvd)
            waitingForReply = False
        #time.sleep(2)

        # Creates box around face in frame
        frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 3)
        frame = cv2.putText(frame, "Location: " + str(xPos) + ", Size: " + str(w), (x,y), font, 1, (255,255,255), 2, cv2.LINE_AA)
    cv2.imshow('Live View', frame)

    # Breaks from loop
    if cv2.waitKey(1) & 0xFF == 27:
        break

arduino.close()
cap.release()
cv2.destroyAllWindows()

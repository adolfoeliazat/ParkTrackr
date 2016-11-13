'''
Created on Nov 11, 2016

@author: User
'''
# Implement multithreading to seperate work between getting image and making the HTTP POST request
import thread

# Imports from Google cloud vision
import argparse
import base64

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from serial import Serial
import math
import time

import numpy as np
import cv2

import ParkingDeck

max_pictures = 3*30
lightInitial = 0
initialDist = 0

def setInitialLight():
    global lightInitial
    byteL = serL.readline();
    byteL = byteL[1:].decode("utf-8")
    count = 5
    sum = 0
    while count > 0:
        time.sleep(0.1)
        light = byteL.strip()
        if(light==''):
            continue
        else:
            light = int(light)
            sum += light
            count = count - 1
    lightInitial = sum/5
            

def setInitialDistance():
    global initialDist

    count = 5
    sum = 0
    
    while count > 0:
        #time.sleep(0.1)
        byteR = serR.readline()
            
        byteR = byteR[1:].decode("utf-8") 
        dist = byteR.strip()
        if(dist == ''):
            continue
            
        else:
            dist = int(dist)
            sum += dist
            count = count - 1

    initialDist = sum/5

def skip_lines(serie):
    for i in range(10):
        serie.readline()
        
# Photo : a cv2 Mat
def label_last_photo_from_opencv(service, image_path):
    print "Now taking label!"

    try:
        # Start construct request
        with open(image_path, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body = {
                'requests' : [{
                    'image' : {
                        'content' : image_content.decode('UTF-8')
                        },
                    'features': [{
                        'type' : 'LABEL_DETECTION',
                        'maxResults' : 1
                        }]
                    }]
                }
            )
        print "request finished!"

        # Start parse response
        response = service_request.execute()

        if response != None:
            if response['responses'] != None:
                if response['responses'][0] != None:
                    if response['responses'][0]['labelAnnotations'] != None:
                        if response['responses'][0]['labelAnnotations'][0]['description'] != None:
                            print "label = "+response['responses'][0]['labelAnnotations'][0]['description']
        else:
            print "Invalid picture."
    except Exception:
        print "Invalid picture."


if __name__ == "__main__":
    # Authenticating with Google to use their Cloud Vision API
    print "Starting credentials!"
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials = credentials)
    print "Ending credentials!"

    cap = cv2.VideoCapture(1)
    photo_ctr = 0

    left_first_ctr = 0
    right_first_ctr = 0

    serL = Serial("COM3", 9600)
    serR = Serial("COM4", 9600)
    setInitialLight()
    setInitialDistance()

    lightInitial = 761
    initialDist = 95

    # print "Initial Light value: {}".format(lightInitial)
    # print "Initial distance : {}".format(initialDist)
    count = 0
    Lon = True
    Ron = True
    oneOff = False
    #time.sleep(0.5)
    
    #print(averageLDist)
    '''
    Lcount = 0
    Rcount = 0
    '''
    print "Started!"
    while True:
        #bit = input("Enter input")
        #ser.write(bit.encode())
        #time.sleep(.1)
        if(Ron):
            '''    
            print(lightInitial)
            print(initialDist)
            '''
            byteR = serR.readline()
            
            byteR = byteR.decode("utf-8") 
            tagR = byteR[:1]
            dist = byteR[1:].strip()

            if(dist != ''):
                
                dist = int(dist)
                # print "Right dist : {}".format(dist)
                diff = dist - initialDist
                #print(str(tagL) + " " + str(distL))
                #print(str(diff))
                
                if(abs(diff) > 50):
                    #print(str(tagL) + " " + str(distL))
                    if(not oneOff):
                        Ron = False
                        print "Right off!"
                        #print(str(tagL) + " off")
                        serR.write(str(2).encode()) 
                        oneOff = not oneOff
                    else:
                        serL.write(str(0).encode()) 
                        print("left first")
                        left_first_ctr += 1
                        Lon = True
                        #time.sleep(.25)

                        # serL.flush()
                        # serR.flush()
                        # time.sleep(2)
                        skip_lines(serL)
                        skip_lines(serR)
                        setInitialDistance()
                        setInitialLight()
                        oneOff = not oneOff
                        continue
                    #oneOff = not oneOff
                    #print(oneOff)
                    
                '''
                else:
                    Lcount = 0
                if(Lcount >= 3):    
                    if(not oneOff):
                        Lon = False
                        #print(str(tagL) + " off")
                        serL.write(str(1).encode()) 
                    else:
                        serR.write(str(0).encode()) 
                        print("right first")
                        Ron = True
                        #time.sleep(.05)
                        setInitialDistances()
                    oneOff = not oneOff 
                '''   
        # else:
        #     pass
            # print "Right is off!"
                
        if(Lon):
            byteL = serL.readline()
            byteL = byteL.decode("utf-8") 
            tagL = byteL[:1]
            light = byteL[1:].strip()
            if(light != ''):
                light = int(light)
                # print "Light value : {}".format(light)
                diff = light - lightInitial 
                 
                #print(str(tagR) + " " + str(distR))
                #print(str(diff))
    
                if(abs(diff) > 50):
                    #print(str(tagL) + " " + str(distL))
                    #Rcount = Rcount + 1
                    if(not oneOff):
                        Lon = False
                        print "Left off!"
                        
                        #print(str(light))
                        serL.write(str(1).encode()) 
                    else:
                        serR.write(str(0).encode())
                    
                        print("right  first")
                        right_first_ctr += 1
                        Ron = True
                        # serL.flush()
                        # serR.flush()
                        # time.sleep(2)
                        skip_lines(serL)
                        skip_lines(serR)
                        setInitialDistance()
                        setInitialLight()
                        
                    oneOff = not oneOff
                    #print(oneOff)  
                '''
                else:
                    Rcount = 0
                if(Rcount >= 3):
                    if(not oneOff):
                        Ron = False
                        #print(str(tagR) + " off")
                        serR.write(str(2).encode()) 
                    else:
                        serL.write(str(0).encode())
                    
                        print("left first")
                        Lon = True
                        #time.sleep(.05)
                        setInitialDistances()
                    oneOff = not oneOff '''
        # else:
        #     pass
            # print "Left is off!"

        # Read frame and show it
        ret, frame = cap.read()
        

        font = cv2.FONT_HERSHEY_SIMPLEX

        if not Lon or not Ron:
            if photo_ctr % 3 == 0 and photo_ctr <= max_pictures:
                filename = "found-images/last_image{}.jpg".format(photo_ctr)
                cv2.imwrite(filename, frame)
                # thread.start_new_thread(label_last_photo_from_opencv, (service, filename))

            photo_ctr += 1
        else:
            photo_ctr = 0
        
        cv2.putText(frame,"Currently tracking : Left first : {} time(s) | Right first : {} time(s)".format(left_first_ctr, right_first_ctr),(7,50), font, 0.5,(0,255,0))
        cv2.imshow("ParkTrackr", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # print "Left first : {} time(s) | Right first : {} time(s)".format(left_first_ctr, right_first_ctr)
        ''' 
        print(Lon)
        print(Ron)  
        '''

    cap.release()
    cv2.destroyAllWindows()

# if __name__ == "__main__":
#     serL = Serial("COM3", 9600)
#     serR = Serial("COM6", 9600)
#     count = 0
#     Lon = True
#     Ron = True
#     oneOff = False
#     #time.sleep(0.5)
#     setInitialDistances()
#     #print(averageLDist)
#     Lcount = 0
#     Rcount = 0
#     while True:
#         #bit = input("Enter input")
#         #ser.write(bit.encode())
#         time.sleep(.25)
#         if(Lon):
#             #print(averageLDist)
#             #print(averageRDist)
#             byteL = serL.readline()
#             
#             byteL = byteL.decode("utf-8") 
#             tagL = byteL[:1]
#             distL = byteL[1:].strip()
#             if(distL != ''):
#                 distL = int(distL)
#                 diff = distL - averageLDist
#                 print(str(tagL) + " " + str(distL))
#                 #print(str(diff))
#                 '''
#                 if(distL < averageLDist - 30 or averageLDist + 30 < distL):
#                     #print(str(tagL) + " " + str(distL))
#                     Lcount = Lcount + 1
#                 else:
#                     Lcount = 0
#                 if(Lcount >= 3):    
#                     if(not oneOff):
#                         Lon = False
#                         #print(str(tagL) + " off")
#                         serL.write(str(1).encode()) 
#                     else:
#                         serR.write(str(0).encode()) 
#                         print("right first")
#                         Ron = True
#                         #time.sleep(.05)
#                         setInitialDistances()
#                     oneOff = not oneOff    
#                 '''
#         if(Ron):
#             byteR = serR.readline()
#             byteR = byteR.decode("utf-8") 
#             tagR = byteR[:1]
#             distR = byteR[1:].strip()
#             if(distR != ''):
#                 distR = int(distR)
#                 diff = distR - averageRDist
#                 print(str(tagR) + " " + str(distR))
#                 #print(str(diff))
#                 '''
#                 if(distR < averageRDist - 20 or averageRDist + 20 < distR):
#                     #print(str(tagL) + " " + str(distL))
#                     Rcount = Rcount + 1
#                 else:
#                     Rcount = 0
#                 if(Rcount >= 3):
#                     if(not oneOff):
#                         Ron = False
#                         #print(str(tagR) + " off")
#                         serR.write(str(2).encode()) 
#                     else:
#                         serL.write(str(0).encode())
#                     
#                         print("left first")
#                         Lon = True
#                         #time.sleep(.05)
#                         setInitialDistances()
#                     oneOff = not oneOff
#                 '''
        
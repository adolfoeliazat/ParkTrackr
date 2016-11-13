# Implement multithreading to seperate work between getting image and making the HTTP POST request
import thread

# Imports from Google cloud vision
import argparse
import base64

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# Import OpenCV
import numpy as np
import cv2


def label_photo_from_file (photo_file):

    # Authenticating with Google
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials = credentials)

    # Start construct request
    with open(photo_file, 'rb') as image:
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

        # Start parse response
        response = service_request.execute()
        label = response['responses'][0]['labelAnnotations'][0]['description']

        # print response['responses'][0]['labelAnnotations']
        print "Found label: {} for {}".format(label, photo_file)

def capture_frame_and_show (cap):
    ret, frame = cap.read()
    
    cv2.imshow("Live Stream", frame)

# Photo : a cv2 Mat
def label_last_photo_from_opencv(service, image_path):
    print "Now taking label!"

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

    # Start parse response
    response = service_request.execute()
    label = response['responses'][0]['labelAnnotations'][0]['description']

    print "Found label: {}".format(label)

def main():
    # Authenticating with Google to use their Cloud Vision API
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials = credentials)

    # Start the video capture object to capture from camera 1
    cap = cv2.VideoCapture(1)

    while (True):
        # Read frame and show it
        ret, frame = cap.read()
        cv2.imshow("Live Stream", frame)

        # Perform tasks based on input queries
        if cv2.waitKey(1) & 0xFF == ord('t'):
            # Save image
            cv2.imwrite("found-images/last_image.jpg", frame)
   
            thread.start_new_thread(label_last_photo_from_opencv, (service, "found-images/last_image.jpg"))
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything's done, release the camera
    cap.release()
    cv2.destroyAllWindows()
    
    # label_photo_from_file("laptop_picture.jpg")

if __name__ == "__main__":
    main()
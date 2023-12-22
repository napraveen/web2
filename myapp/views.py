from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Details
import cv2
import os
# def index(request):
#     return render(request, 'index.html')

# def video(request):
#     cam = cv2.VideoCapture(0) 
#     try: 
#         if not os.path.exists('data'): 
#             os.makedirs('data') 
#     except OSError: 
#         print('Error: Creating directory of data') 

#     currentframe = 0
#     frame_skip = 30 
#     current = 232
#     while True: 
#         ret, frame = cam.read() 

#         if ret: 
#             if currentframe % frame_skip == 0: 
#                 name = './data/frame' + str(current) + '.jpg'
#                 print('Creating...' + name)
#                 cv2.imwrite(name, frame) 
#                 current+=1
            
#             currentframe += 1
#         else: 
#             break
#     cam.release() 
#     return render(request, 'video.html')

# Import necessary modules and functions...
def index(request):
    return render(request, 'index.html')

def start_video(request):
    global video_capture
    video_capture = cv2.VideoCapture(0)

    currentframe = 0
    frame_skip = 30
    current = 0
    if not os.path.exists('data'): 
        os.makedirs('data') 
    while True:
        ret, frame = video_capture.read()

        if ret:
            if currentframe % frame_skip == 0:
                name = './data/frame' + str(current) + '.jpg'
                print('Creating...' + name)
                cv2.imwrite(name, frame)
                current += 1

            currentframe += 1
        else:
            break


    video_capture.release()
    return HttpResponse("Video capturing stopped.")

def stop_video(request):
    global video_capture  # Access the global variable
    video_capture.release()
    return HttpResponse("Video capturing stopped.")


def video (request):
    return render(request, 'video.html')

def monitor (request):
    return render(request, 'monitor.html')
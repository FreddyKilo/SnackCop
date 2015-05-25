#!/usr/bin/env python

import hipchat
import RPi.GPIO as GPIO
import os
import smtplib
from time import sleep
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

PHOTOS_DIR = "/home/pi/Desktop/snackCopPhotos/"
BASE_IMAGE_NAME = "image_{}.jpg"
BASE_VIDEO_NAME = "video_{}.h264"
RECORD_VIDEO = "raspivid -rot 180 -o {} -t {}"
RECORD_LENGTH = 10000
SNAP_PHOTO = "raspistill -rot 180 -o {}"
APPENDED_NUMBER = "image_numbers.txt"
EMAIL_TO = "your email address"
TEXT_TO = "<your number>@<your carrier>.com"

def getFileNum(txt_file):
    """returns a sequential number that reads and writes to
    image_numbers.txt"""
    read_number = open(txt_file, 'r')
    num = int(read_number.read()) + 1
    read_number.close()
    write_number = open(txt_file, 'w')
    str_num = str(num)
    write_number.write(str_num)
    write_number.close()
    read_number = open(txt_file, 'r')
    number = read_number.read()
    read_number.close()
    return number

def getFileName(base, txt_file):
    """returns a file name with an injected sequential integer"""
    number = str(getFileNum(txt_file))
    return base.format(number)

def takePic(file_name):
    os.system(SNAP_PHOTO.format(PHOTOS_DIR + file_name))
    return file_name

def recordVideo(file_name, time):
    os.system(RECORD_VIDEO.format(PHOTOS_DIR + file_name, time))

def emailPic(email):
    file_name = takePic(getFileName(BASE_IMAGE_NAME, APPENDED_NUMBER))
    os.system("/home/pi/email_attach.py " + PHOTOS_DIR + file_name + " " + email + "&")

def sendHipChat():
    chat = hipchat.HipChat(token="<hipcaht token here>")
    room_id = 000000 #room id here
    from_name = 'Frank'
    chat.message_room(room_id, from_name, "@here " + "Somebody is gankin' yo snacks!!", color="red", notify=True)

def motionCheck():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.IN)
    snappingPhotos = False
    while True:
        try:
            input = GPIO.input(7) #listen for signal
            if(input == 1):
                if(not snappingPhotos):
                    sendHipChat()
                    recordVideo(getFileName(BASE_VIDEO_NAME, APPENDED_NUMBER), RECORD_LENGTH)
                emailPic(EMAIL_TO)
                snappingPhotos = True
            else:
                snappingPhotos = False
                sleep(.5)
        except KeyboardInterrupt:
            break

    GPIO.cleanup()

motionCheck()

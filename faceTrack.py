from video import create_capture
from common import clock, draw_str
import serial
import numpy as np
import cv2

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

if __name__ == '__main__':
    ser = serial.Serial(8,9600)
    video_src = 0
    cascade_fn = "haarcascades/haarcascade_frontalface_alt.xml"
    nested_fn  = "haarcascades/haarcascade_eye.xml"
    cascade = cv2.CascadeClassifier(cascade_fn)
    nested = cv2.CascadeClassifier(nested_fn)
    cam = create_capture(video_src)
    tracking = 0
    count = 0
    
    while True:
        ret, img = cam.read()
        vis = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        rects = detect(gray, cascade)
        if not tracking and rects != []:
            x0, y0, x1, y1 = rects[0]
            track_window = (x0, y0, x1-x0, y1-y0)
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX);
            hist = hist.reshape(-1)
            tracking = 1
        elif tracking == 1:
            prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
            prob &= mask
            term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
            if rects != []:
                x0, y0, x1, y1 = rects[0]
                track_window = (x0, y0, x1-x0, y1-y0)
            track_box, track_window = cv2.meanShift(prob, track_window, term_crit)
            x,y,w,h = track_window
            cv2.rectangle(vis, (x,y), (x+w,y+h), 255,2)
            x0, y0, x1, y1 = x, y, x+w, y+h
            midpoint = (x0+x1)/2
            if midpoint >= 320+50:
                ser.write("R")
            elif midpoint <= 320-50:
                ser.write("L")
            else:
                ser.write("F")
            if x0 == 0 or x1 == 640 or y0 == 0 or y1 == 480:
                tracking = 0
            #elif track_box == 0:
            #    tracking = 0
            if count == 100:
                tracking = 0
                count = 0
            count += 1
                
        cv2.imshow('faceTrack', vis)
        
        ch = 0xFF & cv2.waitKey(5)
        if ch == 27:
            break
        if ch == ord('r'):
            tracking = 0
        if ch == ord('a'):
            ser.write("L")
        if ch == ord('d'):
            ser.write("R")
    cv2.destroyAllWindows()

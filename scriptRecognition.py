import cv2
from keras.models import load_model
import numpy as np
from collections import deque

model1 = load_model("devanagari.h5")
print(model1)

#defining the dictonary that maps the output to the letters
letters_count= {0:'CHECK', 1:'1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
                10: 'ka', 11: 'kha', 12: 'ga', 13: 'gha', 14: 'kna', 15: 'cha', 16: 'chha', 17: 'ja', 18: 'jha',
                19:'yna', 20: 'ta', 21: 'tha', 22: 'dha', 23: 'ada', 24: 'na', 
                25: 'ta', 26: 'tha', 27: 'da', 28: 'dha', 29: 'nna', 
                30: 'pa', 31: 'pha', 32: 'ba',33 : 'bha', 34: 'ma', 35: 'yea', 36: 'ra', 37: 'la', 38: 'va', 39: 'sh', 40: 'sha', 41: 'sa', 42: 'ha', 43: 'ksha', 44: 'tra', 45: 'gya'}



#prediction

def keras_process_image(img):
    image_x = 32
    image_y = 32
    img = cv2.resize(img, (image_x, image_y))
    img = np.array(img, dtype=np.float32)
    img = np.reshape(img, (-1, image_x, image_y, 1))
    return img

def keras_predict(model, image):
    processed = keras_process_image(image)
    print("processed: " + str(processed.shape))
    pred_probab = model.predict(processed)[0]
    pred_class = list(pred_probab).index(max(pred_probab))
    return max(pred_probab), pred_class


cap = cv2.VideoCapture(0)
Lower_bLue = np.array([110,50,50])
Upper_blue = np.array([130, 255, 255])
pred_class = 0
pts = deque(maxlen = 512)
blackboard = np.zeros((480, 640, 3), dtype = np.uint8)
digit = np.zeros((200, 200, 3), dtype = np.uint8)

while(cap.isOpened()):
    ret, img = cap.read()
    if ret:
        img = cv2.flip(img, 1)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, Lower_bLue, Upper_blue)
        blur = cv2.medianBlur(mask, 15)
        blur = cv2.GaussianBlur(blur, (5,5), 0)
        thresh = cv2.threshold(blur, 0, 255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        center = None
        if len(cnts) >= 1:
            contour = max(cnts, key=cv2.contourArea)
            if cv2.contourArea(contour) > 250:
                ((x,y), radius) = cv2.minEnclosingCircle(contour)
                cv2.circle(img, (int(x),int(y)), int(radius), (0,255,255), 2)
                cv2.circle(img, center, 5, (0,0,255), -1)
                M = cv2.moments(contour)
                center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
                pts.appendleft(center)

                for i in range(1, len(pts)):
                    if pts[i-1] is None or pts[i] is None:
                        continue
                    cv2.line(blackboard,pts[i-1],pts[i], (255,255,255), 10)
                    cv2.line(img, pts[i-1], pts[i], (0,0,255),5)
        elif len(cnts) == 0:
            if len(pts) != []:
                blackboard_gray = cv2.cvtColor(blackboard, cv2.COLOR_BGR2GRAY)
                blur1 = cv2.medianBlur(blackboard_gray, 15)
                blur1 = cv2.GaussianBlur(blur1, (5,5), 0)
                thresh1 = cv2.threshold(blur1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                blackboard_cnts = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
                if len(blackboard_cnts) >= 1:
                    cnt = max(blackboard_cnts, key = cv2.contourArea)
                    if cv2.contourArea(cnt) > 2000:
                        x,y,w,h = cv2.boundingRect(cnt)
                        digit = blackboard_gray[y:y+h,x:x+w]

                        pred_probab, pred_class = keras_predict(model1, digit)
                        print(pred_class, pred_probab)


            pts = deque(maxlen=512)
            blackboard =  np.zeros((480,640,3), dtype=np.uint8)
        cv2.putText(img, "Conv Network: " + letters_count[pred_class], (10, 470),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,255),2)
        cv2.imshow("frame", img)
        #cv2.imshow("Contours", thresh)
        k = cv2.waitKey(10)
        if k == 27:
            break




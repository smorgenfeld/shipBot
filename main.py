import cv2;
import numpy as np;
import imutils;

def processScreenshot(image):
    img = cv2.imread(image, 1)
    
    lower_red = np.array([0,60,180])
    upper_red = np.array([80,130,255])
    
    
    mask = cv2.inRange(img, lower_red, upper_red)
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    
    cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()
    ratio = 1;
    boundRect = [None]*len(cnts)
    ii = 0;
    for c in cnts:
    	# compute the center of the contour, then detect the name of the
    	# shape using only the contour
        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        #shape = sd.detect(c)
     
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
        
        boundRect[ii] = cv2.boundingRect(c);
        
        # only grab helath bars (will be a certain height, about 13-15 pixels, and will be lower than upper UI)
        if (13 < boundRect[ii][3] < 15 and boundRect[ii][1] > 100):
            cv2.rectangle(img, (int(boundRect[ii][0]), int(boundRect[ii][1])), \
                      (int(boundRect[ii][0]+boundRect[ii][2]), int(boundRect[ii][1]+boundRect[ii][3])), (255,0,0), 2)
            
            # ship center?
            cv2.circle(img, (int(boundRect[ii][0] + 50), int(boundRect[ii][1] + 150)), 10, (255,0,0))
        
            cv2.putText(img, str(boundRect[ii][2]) + ", " + str(boundRect[ii][3]), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        ii += 1;

    
    cv2.imshow("img", img)
    #cv2.imshow("mask", blurred)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        ar = 0;
        if len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
        return str(ar)

#processScreenshot("newMexico_7_5.png")
#processScreenshot("leander_10_6.png")
processScreenshot("ranger_10_8.png")
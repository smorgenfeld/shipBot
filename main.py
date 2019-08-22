import cv2;
import numpy as np;
import imutils;

HEALTHBAR_WIDTH = 92;

def processScreenshot(image):
    img = cv2.imread(image, 1)
    cleanimg = img.copy();
    
    lower_red = np.array([0,60,180])
    upper_red = np.array([100,130,255])
    
    
    mask = cv2.inRange(img, lower_red, upper_red)
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    
    cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    #sd = ShapeDetector()
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
        
        # only grab health bars (will be a certain height, about 13-15 pixels,
        # will be lower than upper UI, and will have the red ship icon above the health bar)
        #cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 5), int(boundRect[ii][1] - 28)), 2, (255,0,0))
        if (13 <= boundRect[ii][3] <= 15 and boundRect[ii][1] > 100 and 
            0 < int(boundRect[ii][1] - 30) < 1080 and 0 < int(boundRect[ii][0] + HEALTHBAR_WIDTH/2) < 1920 and
            blurred[int(boundRect[ii][1] - 28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 5)] > 0):
            
            print(cleanimg[int(boundRect[ii][1] -28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2+1)]);
            
            cv2.rectangle(img, (int(boundRect[ii][0]), int(boundRect[ii][1])), \
                      (int(boundRect[ii][0]+boundRect[ii][2]), int(boundRect[ii][1]+boundRect[ii][3])), (255,0,0), 2)
            
            # ship center?
            cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2), int(boundRect[ii][1] + getBarOffset())), 10, (255,0,0))
            
            # determine ship class
            cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 1), int(boundRect[ii][1] - 28)), 2, (255,0,0))
            cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 1), int(boundRect[ii][1] - 28)), 2, (255,255,0))
            cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 3), int(boundRect[ii][1] - 30)), 2, (0,255,0))
            shipType = "unknown";
            
            caLine = cleanimg[int(boundRect[ii][1] - 28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 1),0];
            bbLine = cleanimg[int(boundRect[ii][1] - 28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 1),0];
            ddLine = cleanimg[int(boundRect[ii][1] - 30), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 3),2];
            cvLine = cleanimg[int(boundRect[ii][1] - 27), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 3),0];
            
            if (ddLine < 150):
                shipType = "DD";
            elif (cvLine < 20):
                shipType = "CA";
            elif (caLine < 20):
                shipType = "CA";
            elif (bbLine < 20):
                shipType = "BB";
            
            cv2.putText(img, str(boundRect[ii][2]) + ", " + str(boundRect[ii][3]) + " " + shipType, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        ii += 1;

    
    cv2.imshow("img", img)
    #cv2.imshow("mask", blurred)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getBarOffset():
    
    return 150;

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

processScreenshot("lightning_5_6.png")
#250

processScreenshot("colorado_6_2.png")
#235

processScreenshot("vlad_7_2.png")
#200

processScreenshot("newMexico_7_5.png")
#175

processScreenshot("kongo_10_3.png")
#145

processScreenshot("leander_10_6.png")
#130

processScreenshot("ranger_10_8.png")
#145

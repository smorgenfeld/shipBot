import cv2, imutils, win32gui, time;
import numpy as np, pytesseract as ocr, directKeys as dk;
from PIL import ImageGrab;

HEALTHBAR_WIDTH = 135;#92 (for 100% UI)
DD = False;
CA = False;
BB = False;
CV = False;

def process(img):
    cleanimg = img.copy();
    
    lower_red = np.array([0,60,180])
    upper_red = np.array([100,130,255])
    
    
    mask = cv2.inRange(img, lower_red, upper_red)
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    
    cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
        if (10 <= boundRect[ii][3] <= 28 and boundRect[ii][1] > 100 and 
            0 < int(boundRect[ii][1] - 30) < 1080 and 0 < int(boundRect[ii][0] + HEALTHBAR_WIDTH/2) < 1920 and
            blurred[int(boundRect[ii][1] - 40), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 5)] > 0):
            
            cv2.rectangle(img, (int(boundRect[ii][0]), int(boundRect[ii][1])), \
                      (int(boundRect[ii][0]+boundRect[ii][2]), int(boundRect[ii][1]+boundRect[ii][3])), (255,0,0), 2)
            
            # ship center?
            cv2.circle(img, (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2), int(boundRect[ii][1] + getBarOffset())), 10, (255,0,0))
            
            # determine ship class      
            shipType = "unknown";
            
            caLine = cleanimg[int(boundRect[ii][1] - 28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 1),1];
            bbLine = cleanimg[int(boundRect[ii][1] - 28), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 1),1];
            ddLine = cleanimg[int(boundRect[ii][1] - 30), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 3),2];
            cvLine = cleanimg[int(boundRect[ii][1] - 27), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 5),1];
            
            if (ddLine < 150):
                shipType = "DD";
            elif (bbLine < 50):
                shipType = "BB";
            elif (caLine < 50 and cvLine > 50):
                shipType = "CA"
            elif (cvLine < 50):
                shipType = "CV";
            
            # get enemy ship distance
            distRect = (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 30), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 5), int(boundRect[ii][1] + 28), int(boundRect[ii][1] + 45))
            cv2.rectangle(img, (distRect[0], distRect[2]), (distRect[1], distRect[3]), (255,0,0), 2)
            
            distImg = cv2.cvtColor(cleanimg[distRect[2]:distRect[3],distRect[0]:distRect[1]], cv2.COLOR_BGR2GRAY);
            # from https://groups.google.com/forum/#!msg/tesseract-ocr/Wdh_JJwnw94/24JHDYQbBQAJ
            # we want the numbers to be about 30 pixels tall for best accuracy, so we scale the image up
            distImg = cv2.resize(distImg,(int(distImg.shape[1]*3),int(distImg.shape[0]*3)))

            distImgT = None;
            dist = -1;
            
            for i in range(190, 100, -10):
                k, distImgT = cv2.threshold(distImg,i,255,cv2.THRESH_BINARY);
                distImgT = cv2.bitwise_not(distImgT);
                dist = ocr.image_to_string(distImgT, config='outputbase digits')
                if (dist != "" and isNumber(dist) and 3 <= len(dist) <= 4 and dist[-2] == "." and 0 <= float(dist) <= 40):
                    break;
            #cv2.imshow("Distance Image", distImgT);
            print("dist: " + dist)
            
            # get enemy name
            nameRect = (int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 - 70), int(boundRect[ii][0] + HEALTHBAR_WIDTH/2 + 70), int(boundRect[ii][1] - 30), int(boundRect[ii][1] - 5))
            cv2.rectangle(img, (nameRect[0], nameRect[2]), (nameRect[1], nameRect[3]), (255,0,0), 2)
            
            nameImg = cv2.cvtColor(cleanimg[nameRect[2]:nameRect[3],nameRect[0]:nameRect[1]], cv2.COLOR_BGR2GRAY);
            nameImg = cv2.resize(nameImg,(int(nameImg.shape[1]*3),int(nameImg.shape[0]*3)))

            nameImgT = None;
            name = "null";
            
            for i in range(190, 100, -10):
                k, nameImgT = cv2.threshold(nameImg,i,255,cv2.THRESH_BINARY);
                nameImgT = cv2.bitwise_not(nameImgT);
                name = ocr.image_to_string(nameImgT)
                if (name != ""):
                    break;
            #cv2.imshow("Distance Image", distImgT);
            print("name: " + name)
            
            cv2.putText(img, str(boundRect[ii][2]) + ", " + str(boundRect[ii][3]) + " " + shipType + " " + dist + " " + name, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            #aim to the center of the ship
            dk.MouseMoveTo(int((boundRect[ii][0] + HEALTHBAR_WIDTH/2)-955), 0)
            aimToDist(dist);
            
        ii += 1;
    
    # get ui stuff
    # get shell flight time
    cv2.rectangle(img, (820, 565), (870, 590), (255,0,0), 2)
    seconds = getSeconds(cleanimg);
    
    #cv2.imshow("Seconds Image", secImgT);
    # get aiming distance
    cv2.rectangle(img, (1020, 565), (1065, 590), (255,0,0), 2)
    seconds = getAimDist(cleanimg);
    #print("Seconds: " + str(seconds));
    #print("Aiming Distance: " + str(aimDist));

    #cv2.imshow("img", img)
    #cv2.imshow("mask", blurred)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def getSeconds(image):
    secImg = cv2.cvtColor(image[565:590,820:870], cv2.COLOR_BGR2GRAY);
    
    secImg = cv2.resize(secImg,(int(secImg.shape[1]*1.5),int(secImg.shape[0]*1.5)))
    
    secImgT = None;
    seconds = -1;
    
    for i in range(190, 100, -10):
        k, secImgT = cv2.threshold(secImg,i,255,cv2.THRESH_BINARY);
        secImgT = cv2.bitwise_not(secImgT);
        seconds = ocr.image_to_string(secImgT, config='outputbase digits')
        if (seconds != "" and isNumber(seconds) and 4 <= len(seconds) <= 5 and seconds[-3] == "." and 0 <= float(seconds) <= 40):
            break;
    return seconds;

def getAimDist(image):
     # get aiming distance
    #cv2.rectangle(img, (1020, 565), (1065, 590), (255,0,0), 2)
    aimDistImg = cv2.cvtColor(image[565:590,1020:1065], cv2.COLOR_BGR2GRAY);
    
    aimDistImg = cv2.resize(aimDistImg,(int(aimDistImg.shape[1]*1.5),int(aimDistImg.shape[0]*1.5)))
    
    aimDistImgT = None;
    aimDist = -1;
    
    for i in range(190, 100, -10):
        k, aimDistImgT = cv2.threshold(aimDistImg,i,255,cv2.THRESH_BINARY);
        aimDistImgT = cv2.bitwise_not(aimDistImgT);
        aimDist = ocr.image_to_string(aimDistImgT, config='outputbase digits')
        if (aimDist != "" and isNumber(aimDist) and 4 <= len(aimDist) <= 5 and aimDist[-3] == "." and 0 <= float(aimDist) <= 40):
            break;
    
    print("Aiming Distance: " + str(aimDist));
    return aimDist;

def aimToDist(goal):
    minDelta = 0.05;
    for i in range(10):
        delta = float(goal) - float(getAimDist(getScreen()));
        print(delta)
        if (abs(delta) < minDelta):
            print("done in " + str(i+1) + " steps")
            break;
        else:
            dk.MouseMoveTo(0,int(-delta * 64))

def processScreenshot(image):
    process(cv2.imread("screenshots/"+image, 1));

def getScreen():
    hwnd = win32gui.FindWindow(None, r'World of Warships')
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    bbox = win32gui.GetWindowRect(hwnd)
    #bbox[2] -= 5;
    bbox = (bbox[0] + 10, bbox[1] + 32, bbox[2] - 10, bbox[3] - 10)
    img = ImageGrab.grab(bbox)
    
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def getBarOffset():
    
    return 200;

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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

#DD = True;
#CA = True;
#BB = True;
#CV = True;
#processScreenshot("lightning_5_6.png")
#processScreenshot("leander_10_6.png")
#processScreenshot("test1.png")
#processScreenshot("republique_11_6.png")

time.sleep(3);
#aimToDist(9);
process(getScreen())

if (DD):
    #does't work
    processScreenshot("lightning_5_6.png")
    #250
    
    processScreenshot("kagero_8_2.png")
    #110

if (CA):
    processScreenshot("cleveland_7_0.png")
    #190
    
    processScreenshot("belfast_7_4.png")
    #175
    
    processScreenshot("belfast_7_4_turned.png")
    #175
    
    
    processScreenshot("moskva_10_4.png")
    #170
    
    #does't work
    processScreenshot("leander_10_6.png")
    #130
     
    processScreenshot("edinburgh_12_3.png")
    #115


if (BB):
    processScreenshot("colorado_6_2.png")
    #235
    
    processScreenshot("vlad_7_2.png")
    #200
    
    processScreenshot("newMexico_7_5.png")
    #175
    
    processScreenshot("kongo_10_3.png")
    #145
    
    processScreenshot("republique_11_6.png")
    #170
    
if (CV):
    processScreenshot("ranger_10_8.png")
    #145


import numpy as np
import pyautogui
import cv2
import requests
import time
from array import array
import pytesseract as tess
import json
import re
tess.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
maxCycle = 1
filename = 'xx.png' 
thresholdGlobal = 0.9
arrayOut = []
strInfoPrev = ''
array1Texts = []
def DoScreenshot():
    pyautogui.screenshot(filename)
def cropMainWindow(img):
    y = 90
    x = 250
    w = 1920 - 500
    h = 1080 - 125
    crop = img[y:y+h, x:x+w]
    return crop
def getArrayTexts(img_grey_invert):
    txtdata = tess.image_to_data(img_grey_invert)
    txtlines = txtdata.splitlines()
    txts = []
    index = 0
    for txtline in txtlines:
        if index > 0:
            params = txtline.split('\t')
            name = params[11].strip()
            if len(name) > 0:
                json = {
                    "id": len(txts) + 1,
                    "x": int(params[6]), 
                    "y": int(params[7]), 
                    "w": int(params[8]), 
                    "h": int(params[9]), 
                    "txt": name
                }
                txts.append(json)
        index = index + 1
    return txts
def getAllPlayers(txts):
    index = 0
    for txt in txts:
        if "BB" in txt["txt"]:
            if len(txt["txt"]) > 2:
                indexSumma = index
            else:
                indexSumma = searchForSumma(txts, index)
            if indexSumma > 0:
                summa = txts[indexSumma]["txt"]
                indexName = searchForName(txts, indexSumma, index)
                if indexName > 0:
                    name = txts[indexName]["txt"].strip()
                    addPlayer(name, summa, txts[index]["x"], txts[index]["y"])
        index = index + 1
def getAllTotalWords(txts):
    arrTotalWords = []
    for txt in txts:
        if "Total" in txt["txt"]:
            arrTotalWords.append(txt)
    return arrTotalWords
def getAllPotWords(txts):
    arrPotWords = []
    for txt in txts:
        if "Pot" in txt["txt"]:
            arrPotWords.append(txt)
    return arrPotWords
def getTotalPotCoords(txts):
    arrTotalWords = getAllTotalWords(txts)
    arrPotWords = getAllPotWords(txts)
    for total in arrTotalWords:
        x = total["x"] + total["w"]
        y = total["y"]
        for pot in arrPotWords:
            difX = abs(pot["x"] - x)
            difY = abs(pot["y"] - y)
            if difX < 20 and difY < 10:
                return total
def searchForName(arr, indexSumma, indexBB):
    delta = 30
    xMiddle = (arr[indexSumma]["x"] + (arr[indexBB]["x"] + arr[indexBB]["w"])) / 2
    yMiddle = arr[indexBB]["y"] - arr[indexBB]["h"] * 2
    i = indexSumma - 1
    while i > -1:
        name = arr[i]["txt"].strip()
        if name != '' and name != ',' and name != ':' and name != ';' and name != 'BB' and name != 'Raise':
            y = arr[i]["y"]
            if abs(y - yMiddle) < delta:
                x = arr[i]["x"] + (arr[i]["w"] / 2)
                if abs(x - xMiddle) < delta:
                    return i
        i = i - 1
    return 0
def searchForSumma(arr, index):
    yBB = arr[index]["y"]
    xBB = arr[index]["x"]
    wBB = arr[index]["w"]
    hBB = arr[index]["h"]
    height = hBB / 2
    width = wBB * 3
    i = index - 1
    while i > -1:
        y = arr[i]["y"]
        if abs(y - yBB) < height:
            x = arr[i]["x"]
            if abs(x - xBB) < width:
                num = arr[i]["txt"]
                try:
                    float(num)
                    return i
                except ValueError:
                    z = 0
        i = i - 1
    return 0
def addPlayer(name, summa, x, y):
    if name != '':
        flag = True
        for player in arrayOut:
            if player["name"] == name:
                flag = False
                break
            if abs(player["x"] - x) < 10 and abs(player["y"] - y) < 10:
                flag = False
                break
        if flag:
            arrayOut.append(
                {
                    "name": name, 
                    "summa": summa,
                    "x": x,
                    "y": y
                })
def getTemplatePlaces(img_gray, template, threshold = 0.8):
    arrayPlaces = []
    w2, h2 = template.shape[::-1]
    res2 = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where( res2 >= threshold)
    for pt in zip(*loc[::-1]):
        arrayPlaces.append(pt)
    return arrayPlaces
def getMinXY(arrayButtonspt):
    minxButton = 99999
    minyButton = 99999
    for item in arrayButtonspt:
        if item[0] < minxButton:
            minxButton = item[0]
        if item[1] < minyButton:
            minyButton = item[1]
    return {
        "x": minxButton,
        "y": minyButton
    }
def doRoundButtonSelected(img, arrayButtonspt):
    template3 = getRoundButtonTemplate()
    w3, h3 = template3.shape[::-1]
    for pt in arrayButtonspt:
        cv2.rectangle(img, pt, (pt[0] + w3, pt[1] + h3), (0,0,255), 2)
def getRoundButtonTemplate():
    return cv2.imread('./images/templates/roundbutton.png', 0)
def getRoundButtonPlaces(img_gray):
    return getTemplatePlaces(img_gray, getRoundButtonTemplate(), 0.8)
def doBackCardsSelected(img, arrayButtonspt):
    template3 = getDealerTemplate()
    w3, h3 = template3.shape[::-1]
    for pt in arrayButtonspt:
        cv2.rectangle(img, pt, (pt[0] + w3, pt[1] + h3), (0,0,255), 2)
def getBackCardsTemplate():
    return cv2.imread('./images/templates/backcards.png', 0)
def getBackCardsPlaces(img_gray):
    return getTemplatePlaces(img_gray, getBackCardsTemplate(), 0.9)
def doAllTotalPotSelected(img):
    cv2.rectangle(img, (580, 275), (840, 320), (0,0,255), 2)
def getTotalPotWords(arrayTexts):
    rectangle = {
        "x1": 580,
        "y1": 285,
        "x2": 840,
        "y2": 330
    }
    return findTxtInsideRectangle(arrayTexts, rectangle)
def getSummaTotalPotWords(img, arrayTexts):
    arrayTotalPotWords = getTotalPotWords(arrayTexts)
    for txt in arrayTotalPotWords:
        doWordSelected(img, txt)
    arrTxtSummaTotalPot = []
    for txt in arrayTotalPotWords:
        doWordSelected(img, txt)
        str = '' + txt["txt"]
        str = str.replace(".’","").replace(":","").replace("Total","").replace("Pot","").replace("BB","").strip()
        if len(str) > 0:
            arrTxtSummaTotalPot = addTextIfNotExist(arrTxtSummaTotalPot, str)
    strSummaTotalPot = ''
    for txt in arrTxtSummaTotalPot:
        strSummaTotalPot = strSummaTotalPot + txt
    return strSummaTotalPot
def findTxtInsideRectangle(arrayTexts, rectangle):
    arrayTxtOut = []
    for txt in arrayTexts:
        if rectangle["x1"] < txt["x"] and rectangle["y1"] < txt["y"]:
            if rectangle["x2"] > txt["x"]+txt["w"] and rectangle["y2"] > txt["y"]+txt["h"]:
                arrayTxtOut.append(txt)
    return arrayTxtOut
def doWordSelected(img, txt):
    cv2.rectangle(img, (txt["x"], txt["y"]), (txt["x"]+txt["w"], txt["y"]+txt["h"]), (0,0,255), 2)
def doRectangleSelected(img, pt):
    cv2.rectangle(img, (pt["x"], pt["y"]), (pt["x"]+pt["w"], pt["y"]+pt["h"]), (0,0,255), 2)
def doBoxSelected(img, pt):
    cv2.rectangle(img, (pt["x1"], pt["y1"]), (pt["x2"], pt["y2"]), (0,0,255), 2)
def doDealerSelected(img, pt):
    template3 = getDealerTemplate()
    w3, h3 = template3.shape[::-1]
    cv2.rectangle(img, pt, (pt[0] + w3, pt[1] + h3), (0,0,255), 2)
def getDealerTemplate():
    return cv2.imread('./images/templates/dealer3.png', 0)
def getDealerPlaces(img_gray):
    return getTemplatePlaces(img_gray, getDealerTemplate(), 0.8)
def setDealerPlayer(dealerpt, arrayPlayers):
    indexPlayer = -1
    if len(dealerpt) > 0 and len(arrayPlayers) > 0:
        minDistance = 99999999
        index = 0
        for item in arrayPlayers:
            distance = getDistance(item, dealerpt)
            if distance < minDistance:
                minDistance = distance
                indexPlayer = index
            index = index + 1
    if len(arrayPlayers) > 0 and indexPlayer > -1:
        arrayPlayers[indexPlayer]["isDealer"] = True
def getRedButtonTemplate():
    return cv2.imread('./images/templates/butstart2.png', 0)
def doRedButtonsSelected(img, arrayButtonspt):
    template3 = getRedButtonTemplate()
    w3, h3 = template3.shape[::-1]
    w3 = 180    
    for pt in arrayButtonspt:
        cv2.rectangle(img, pt, (pt[0] + w3, pt[1] + h3), (0,0,255), 2)
def getRedButtonsPlaces(img_gray):
    return getTemplatePlaces(img_gray, getRedButtonTemplate(), 0.8)
def doCardsSelected(img, arrayPlaces):
    w = 90
    h = 30
    for pt in arrayPlaces:
        if (len(pt) > 0):
            cv2.rectangle(img, (pt["x"]-100, pt["y"]-40), (pt["x"] + w, pt["y"] + h), (0,0,255), 2)
def lookfor(img, template):
    arraypt = []
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = thresholdGlobal
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        arraypt.append(pt)
    return arraypt
def drawRectangles(img, arraypt, template):
    w, h = template.shape[::-1]
    for pt in arraypt:
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    return img
def getSuit(index):
    if (index == 0):
        return 'h'
    if (index == 1):
        return 's'
    if (index == 2):
        return 'c'
    if (index == 3):
        return 'd'
def getCost(index):
    if (index == 0):
        return '2'
    if (index == 1):
        return '3'
    if (index == 2):
        return '4'
    if (index == 3):
        return '5'
    if (index == 4):
        return '6'
    if (index == 5):
        return '7'
    if (index == 6):
        return '8'
    if (index == 7):
        return '9'
    if (index == 8):
        return 'T'  
    if (index == 9):
        return 'J'
    if (index == 10):
        return 'Q'
    if (index == 11):
        return 'K'
    if (index == 12):
        return 'A'
def superTableCards(imgCropTableCards, imgCropTableCardsGray):
    arrayCosts = ['cost2','cost3','cost4','cost5','cost6','cost7','cost8','cost9','cost10','costJ','costQ','costK','costA' ]
    arrayCostPlaces = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
    arrayOutCostPlaces = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
    index = 0
    for cost in arrayCosts:
        template = cv2.imread('./images/templates/' + cost + '.png', 0)
        w, h = template.shape[::-1]
        arrayCostPlaces[index] = lookfor(imgCropTableCardsGray, template)
        for place in arrayCostPlaces[index]:
            x1, y1 = place
            flag = True
            for outPlace in arrayOutCostPlaces[index]:
                x2, y2 = outPlace
                if (abs(x1 - x2) < w / 2):
                    if (abs(y1 - y2) < h / 2):
                        flag = False
                        break
            if flag:
                arrayOutCostPlaces[index].append(place)
        imgCropTableCards = drawRectangles(imgCropTableCards, arrayOutCostPlaces[index], template)
        index = index + 1
    arraySuits = ['heart','spread','crest','diamond']
    arraySuitPlaces = [[], [], [], []]
    arrayOutSuitPlaces = [[], [], [], []]
    index = 0
    for suit in arraySuits:
        template = cv2.imread('./images/templates/' + suit + '.png', 0)
        w, h = template.shape[::-1]
        arraySuitPlaces[index] = lookfor(imgCropTableCardsGray, template)
        for place in arraySuitPlaces[index]:
            x1, y1 = place
            flag = True
            for outPlace in arrayOutSuitPlaces[index]:
                x2, y2 = outPlace
                if (abs(x1 - x2) < w / 2):
                    if (abs(y1 - y2) < h / 2):
                        flag = False
                        break
            if flag:
                arrayOutSuitPlaces[index].append(place)
        imgCropTableCards = drawRectangles(imgCropTableCards, arrayOutSuitPlaces[index], template)
        index = index + 1
    arrayOut = [{},{},{},{},{}]
    minXPrev = 0
    indexOut = 0
    for card in arrayOut:
        index = 0
        minX = 99999
        minY = 99999
        indexMin = -1
        for costs in arrayOutCostPlaces:
            for cost in costs:
                x, y = cost
                if minX > x and minXPrev < x:
                    minX = x
                    minY = y
                    indexMin = index              
            index = index + 1
        if indexMin > -1:
            arrayOut[indexOut] = {
                "x": minX,
                "y": minY,
                "cost": getCost(indexMin),
                "suit": ""
            }
            minXPrev = minX
        indexOut = indexOut + 1
    deltaX = 10
    indexOut = 0
    for card in arrayOut:
        if len(card) > 0:
            xCard = card["x"]    
            index = 0
            for suits in arrayOutSuitPlaces:        
                for suit in suits:
                    x, y = suit
                    if abs(xCard - x) < deltaX:
                        arrayOut[indexOut]["suit"] = getSuit(index)
                index = index + 1
        indexOut = indexOut + 1
    return arrayOut
def makeInfoHandCards(arrayHandCards):
    strHandCards = ''
    for card in arrayHandCards:
        if len(card) > 0:
            strHandCards = strHandCards + "[" + card["cost"] + card["suit"] + "] "
    return strHandCards.strip()
def makeInfoTableCards(arrayTableCards):
    strTableCards = ''
    for card in arrayTableCards:
        if len(card) > 0:
            strTableCards = strTableCards + "[" + card["cost"] + card["suit"] + "] "
    return strTableCards.strip()
def makeInfoPlayers(arrayPlayers, arrayPositions):
    outPlayers = []
    index = 0
    for player in arrayPlayers:
        if len(player) > 0:
            name = player["name"]
            summa = player["summa"].replace("BB", "")
            pos = ""
            if 'isHaveCards' in player:
                pos = arrayPositions[index]
            else:
                pos = "---"
            out = "[" + pos + "]  " + getBlancs(str(summa) + " BB", 12) + str(name)
            outPlayers.append(out)
        index = index + 1
    return outPlayers
def contrast(img, param):
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=param, tileGridSize=(6,6))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return final
def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
    return buf
def getNamePlayerByPlace(coords, arrTexts):
    x1 = coords["x1"]
    y1 = coords["y1"]
    x2 = coords["x1"] + 200
    y2 = coords["y1"] + 50
    for txt in arrTexts:
        if txt["x"] > x1 and txt["y"] > y1:
            if txt["x"] < x2 and txt["y"] < y2:
                str = txt["txt"].strip()
                if str != ":" and str != "." and str != "," and str != "=" and str != "@":
                    return txt["txt"]
    return "..."
def getPlayerByPlace(coords, arrPlayers, arrTexts):
    x1 = coords["x1"]
    y1 = coords["y1"]
    x2 = coords["x2"]
    y2 = coords["y2"]
    for player in arrPlayers:
        if player["x"] > x1 and player["y"] > y1 and player["x"] < x2 and player["y"] < y2:
            str = player["name"].strip()
            if str == ":" or str == "." or str == "," or str == "=" or str == "@":
                player["name"] = getNamePlayerByPlace(coords, arrTexts)
            return player
    return {
        "name": getNamePlayerByPlace(coords, arrTexts),
        "summa": ""
    }
def getCards(arrayCards):
    return arrayCards
def getDistance(point1, point2):
    xDiff = abs(point1["x"] - point2["x"])
    yDiff = abs(point1["y"] - point2["y"])
    return (xDiff + yDiff)
def setPlayersWithCards(arrayBackCardsPoints, arrPlayers):
    for player in arrPlayers:
        for cardPlace in arrayBackCardsPoints:
            distance = getDistance(player, {"x":cardPlace[0], "y":cardPlace[1]})
            if (distance < 200):
                player["isHaveCards"] = True
def getTablePositions(countPlayers):
    return [" BU"," SB"," BB","UTG"," MP"," CO"]
def getShiftedTablePositions(countPlayers, shift):
    arrTablePositions = getTablePositions(countPlayers)
    arrOut = []
    count = len(arrTablePositions) - shift
    while(count < len(arrTablePositions)):
        arrOut.append(arrTablePositions[count])
        count = count + 1
    count = 0
    while(count < (len(arrTablePositions) - shift)):
        arrOut.append(arrTablePositions[count])
        count = count + 1
    return arrOut
def getDealer(arrayPlayers):
    index = 0
    for player in arrayPlayers:
        if 'isDealer' in player:
            if (player["isDealer"]):
                return index
        index = index + 1
    return 0
def getBlancs(str, count):
    while len(str) < count:
        str = str + " "
    return str
def getOutInfo(arrayPlayers, arrayPositions, arrayMyCardsOut, arrayTableOut, summaTotalPot, arrayRedButtons, arrayControls):
    str = ""
    arrayInfoPlayers = makeInfoPlayers(arrayPlayers, arrayPositions)
    for info in arrayInfoPlayers:
        str = str + "\n" + info
    strHandCards = makeInfoHandCards(arrayMyCardsOut)
    str = str + "\n" + "Карты в руке:  " + strHandCards
    strTableCards = makeInfoTableCards(arrayTableOut)
    str = str + "\n" + "Карты на столе:  " + strTableCards
    if len("" + summaTotalPot) > 0:
        summaTotalPot = summaTotalPot + " BB"
    str = str + "\n" + "Общий банк: " + summaTotalPot
    if len(arrayRedButtons) > 0:
        strRedButtons = ""
        for button in arrayRedButtons:
            if len(button) > 0:
                strRedButtons = strRedButtons + "[" + button + "] "
        if len(strRedButtons) > 0:
            str = str + "\n" + "Кнопки: " + strRedButtons
            strControls = ""
            for control in arrayControls:
                strControls = strControls + "[" + control + "] "
            if len(strControls) > 0:
                strControls = strControls + "(*)"
                str = str + "\n" + "Управление: " + strControls
    return str
def getJsonCards(arrCards):
    arrJsonOutCards = []
    for card in arrCards:
        if len(card) > 0:
            arrJsonOutCards.append({
                "cost": card["cost"],
                "suit": card["suit"]
            })
    return arrJsonOutCards
def getJsonPlayers(arrPlayers, arrPositions):
    arrJsonOutPlayers = []
    index = 0
    for player in arrPlayers:
        if len(player) > 0:
            arrJsonOutPlayers.append({
                "name": player["name"],
                "stack": player["summa"],
                "position": arrPositions[index].strip(),
                "isHaveCards": player.get('isHaveCards', False)
            })
        index = index + 1
    return arrJsonOutPlayers
def getOutJson(intDealer, arrayPlayers, arrayPositions, arrayMyCardsOut, arrayTableOut, summaTotalPot, arrayRedButtons, arrayControls):
    jsonOut = {
        "players": getJsonPlayers(arrayPlayers, arrayPositions),
        "herocards": getJsonCards(arrayMyCardsOut),
        "tablecards": getJsonCards(arrayTableOut),
        "totalpot": summaTotalPot,
        "dealer": (intDealer + 1)
    }
    if len(arrayRedButtons) > 0:
        jsonRedButtons = []
        for button in arrayRedButtons:
            if len(button) > 0:
                jsonRedButtons.append(button)
        jsonOut["redbuttons"] = jsonRedButtons
        jsonControls = []
        for control in arrayControls:
            if len(control) > 0:
                jsonControls.append(control)
        jsonOut["controls"] = jsonControls
    return jsonOut
def getTitleControl1(image):
    coords = {"x":830,"y":788,"w":70,"h":53}
    return getTitleControl(coords, image)
def getTitleControl2(image):
    coords = {"x":905,"y":788,"w":70,"h":53}
    return getTitleControl(coords, image)
def getTitleControl3(image):
    coords = {"x":980,"y":788,"w":70,"h":53}
    return getTitleControl(coords, image)
def getTitleControl4(image):
    coords = {"x":1060,"y":788,"w":65,"h":53}
    return getTitleControl(coords, image)
def getTitleControl5(image):
    coords = {"x":1130,"y":795,"w":115,"h":45}
    return getTitleControl(coords, image)
def getTitleControl(coords, image):
    arrTitleTxts = []
    for txt in array1Texts:
        print(txt)
        if txt["x"] > coords["x"] and txt["y"] > coords["y"]:
            if txt["x"] < coords["x"]+coords["w"] and txt["y"] < coords["y"]+coords["h"]:
                arrTitleTxts = addIfNotExist(arrTitleTxts, txt)
    str = ""
    for txt in arrTitleTxts:
        str = str + " " + txt["txt"]
    str = str.strip()
    if len(str) > 0:        
        doRectangleSelected(image, coords)
    coords["txt"] = str
    return coords
def addIfNotExist(arrItems, addItem):
    addItem["txt"] = addItem["txt"].replace("_","").replace("-","").replace("—","").replace(">","").strip()
    for item in arrItems:
        if item["txt"] == addItem["txt"]:
            return arrItems
    arrItems.append(addItem)
    return arrItems
def addTextIfNotExist(arrItems, addItem):
    for item in arrItems:
        if item == addItem:
            return arrItems
    arrItems.append(addItem)
    return arrItems
def cropPlayerRegion(img, coords):
    y = coords["y"]
    x = coords["x"]
    w = coords["w"]
    h = coords["h"]
    crop = img[y:y+h, x:x+w]
    return crop
def getOnlyLettersAndNumbers(str):    
    return re.sub(r'[^a-zA-Z0-9,. ]+', '', str)
def getPlayerFromPlace(img, coords):
    doRectangleSelected(image, coords)
    cropPlayer = cropPlayerRegion(img_grey_invert3, coords)
    arrayPlayerTexts = getArrayTexts(cropPlayer)
    minY = 40
    strPlayerName = ''
    for txt in arrayPlayerTexts:
        if txt["y"] < minY:
            strPlayerName = strPlayerName + txt["txt"]
    strPlayerName = getOnlyLettersAndNumbers(strPlayerName)
    strSumma = ''
    for txt in arrayPlayerTexts:
        if txt["y"] > minY:
            strSumma = strSumma + txt["txt"].replace("BB","").strip()
    strSumma = getOnlyLettersAndNumbers(strSumma)
    return {
        "name": strPlayerName,
        "summa": strSumma,
        "x": coords["x"] + round(coords["w"] / 2),
        "y": coords["y"] + round(coords["h"] / 2)
    }
def getSummaTotalPotFromPlace(image):
    coords = {
        "x":580,
        "y":285,
        "w":260,
        "h":45
    }
    doRectangleSelected(image, coords)
    cropPlayer = cropPlayerRegion(img_grey_invert1, coords)
    arrayWords = getArrayTexts(cropPlayer)
    strSumma = ''
    for word in arrayWords:
        strSumma = strSumma + word["txt"].replace("_","").replace("|","").replace(">","").replace(":","").replace("Total","").replace("Pot","").replace("BB","")
    return strSumma
def getAllOutPlayers(image):
    arrayPlayerz = []
    widthPlayer = 240
    heightPlayer = 80
    coords = {
        "x":590,
        "y":835,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    coords = {
        "x":0,
        "y":650,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    coords = {
        "x":45,
        "y":210,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    coords = {
        "x":590,
        "y":105,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    coords = {
        "x":1130,
        "y":210,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    coords = {
        "x":1180,
        "y":650,
        "w":widthPlayer,
        "h":heightPlayer
    }
    arrayPlayerz.append(getPlayerFromPlace(image, coords))
    return arrayPlayerz
def cropHeroCards(img, coords):
    y = coords["y"]
    x = coords["x"]
    w = coords["w"]
    h = coords["h"]
    crop = img[y:y+h, x:x+w]
    return crop
def getHeroCards():
    global thresholdGlobal
    coordsMyBB = {
        "y":680,
        "x":580,
        "h":120,
        "w":200
    }
    doRectangleSelected(image, coordsMyBB)
    imgCropMyCards = cropHeroCards(image, coordsMyBB)
    imgCropMyCardsGray = cv2.cvtColor(imgCropMyCards, cv2.COLOR_BGR2GRAY)
    thresholdGlobal = 0.82
    return superTableCards(imgCropMyCards, imgCropMyCardsGray)
def cropTableCards(img, coords):
    y = coords["y"]
    x = coords["x"]
    w = coords["w"]
    h = coords["h"]
    crop = img[y:y+h, x:x+w]
    return crop
def getTableCards():
    global thresholdGlobal
    coordsTotal = {
        "y":330,
        "x":380,
        "h":100,
        "w":600
    }
    doRectangleSelected(image, coordsTotal)
    imgCropTableCards = cropTableCards(image, coordsTotal)
    imgCropTableCardsGray = cv2.cvtColor(imgCropTableCards, cv2.COLOR_BGR2GRAY)
    thresholdGlobal = 0.9
    return superTableCards(imgCropTableCards, imgCropTableCardsGray)
def getControls():
    arrayButControls = []
    coord = {"x":820,"y":780,"w":590,"h":70}
    doRectangleSelected(image, coord)
    imgCropTableCards = cropTableCards(image, coord)
    imgCropTableCardsGray = cv2.cvtColor(imgCropTableCards, cv2.COLOR_BGR2GRAY)
    img_grey_invert1z = cv2.bitwise_not(imgCropTableCardsGray)
    arrayTexts = getArrayTexts(img_grey_invert1z)
    coords = {"x":10,"y":0,"w":70,"h":53}
    title = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    arrayButControls.append(title)
    coords = {"x":88,"y":0,"w":70,"h":53}
    title = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    arrayButControls.append(title)
    coords = {"x":170,"y":0,"w":70,"h":53}
    title = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    arrayButControls.append(title)
    coords = {"x":240,"y":0,"w":70,"h":53}
    title = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    arrayButControls.append(title)
    """
    arrayRoundButtonPlaces = getRoundButtonPlaces(img_grey1)
    doRoundButtonSelected(image, arrayRoundButtonPlaces)
    """
    return arrayButControls
def getTitleControla(coords, image, arrTexts):
    arrTitleTxts = []   
    for txt in arrTexts:
        if txt["x"] > coords["x"] and txt["y"] > coords["y"]:
            if txt["x"] < coords["x"]+coords["w"] and txt["y"] < coords["y"]+coords["h"]:
                arrTitleTxts = addIfNotExist(arrTitleTxts, txt)
    str = ""
    for txt in arrTitleTxts:
        str = str + " " + txt["txt"]
    return str.strip()
def getButtons():
    arrayRedButtons = []
    coord = {"x":820,"y":850,"w":590,"h":130}
    doRectangleSelected(image, coord)
    imgCropTableCards = cropTableCards(image, coord)
    imgCropTableCardsGray = cv2.cvtColor(imgCropTableCards, cv2.COLOR_BGR2GRAY)
    img_grey_invert1z = cv2.bitwise_not(imgCropTableCardsGray)
    arrayTexts = getArrayTexts(img_grey_invert1z)
    coords = {"x":30,"y":0,"w":70,"h":88}
    title1 = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    coords = {"x":240,"y":0,"w":80,"h":88}
    title2 = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    coords = {"x":430,"y":0,"w":70,"h":88}
    title3 = getTitleControla(coords, img_grey_invert1z, arrayTexts)
    if (len(title3) > 0 or len(title2)) and len(title1) == 0:
        title1 = "Fold"
    if len(title3) > 0 and len(title2) == 0:
        title2 = "Call"
    if len(title1) > 0:
        arrayRedButtons.append(title1)
    if len(title2) > 0:
        arrayRedButtons.append(title2)
    if len(title3) > 0:
        arrayRedButtons.append(title3)        
    return arrayRedButtons
indexCycle = 0
while indexCycle < maxCycle:
    arrayOut = []
    txts = []
    image = cv2.imread(filename)
    ticks = time.time_ns()
    inFileName = "./in/"+str(ticks)+".png"
    cv2.imwrite(inFileName, image)
    image = cropMainWindow(image)
    img_grey1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_grey_invert1 = cv2.bitwise_not(img_grey1)
    """
    img_contrast2 = contrast(image, 2.0)
    img_grey2 = cv2.cvtColor(img_contrast2, cv2.COLOR_BGR2GRAY)
    img_grey_invert2 = cv2.bitwise_not(img_grey2)
    """
    img_contrast3 = apply_brightness_contrast(image, brightness = 1, contrast = 100)
    img_grey3 = cv2.cvtColor(img_contrast3, cv2.COLOR_BGR2GRAY)
    img_grey_invert3 = cv2.bitwise_not(img_grey3)
    arrayPlayerz = getAllOutPlayers(img_grey_invert1)
    countPlayers = 0
    for player in arrayPlayerz:
        if len(player["name"]) > 0 and len(player["summa"]) > 0:
            countPlayers = countPlayers + 1
    if countPlayers > 0:
        arrayDealerButtonPlaces = getDealerPlaces(img_grey1)
        coordDealerButton = getMinXY(arrayDealerButtonPlaces)
        doDealerSelected(image, (coordDealerButton["x"], coordDealerButton["y"]))
        setDealerPlayer(coordDealerButton, arrayPlayerz)
        summaTotalPot = getSummaTotalPotFromPlace(image)
        arrayBackCardsPLaces = getBackCardsPlaces(img_grey1)
        doBackCardsSelected(image, arrayBackCardsPLaces)
        setPlayersWithCards(arrayBackCardsPLaces, arrayPlayerz)
        arrayHeroCards = getHeroCards()
        arrayTableCards = getTableCards()
        arrayPlayerz[0]["isHaveCards"] = True
        dealerPlayer = getDealer(arrayPlayerz)
        arrayPositions = getShiftedTablePositions(len(arrayPlayerz), dealerPlayer)
        arrayButtons = getButtons()
        arrayControls = []
        if len(arrayButtons) > 0:
            arrayControls = getControls()
        strInfo = getOutInfo(arrayPlayerz, arrayPositions, arrayHeroCards, arrayTableCards, summaTotalPot, arrayButtons, arrayControls)
        if (strInfo != strInfoPrev):
            print("\n")
            print(ticks)
            print(strInfo)
            strInfoPrev = strInfo
            jsonInfo = getOutJson(dealerPlayer, arrayPlayerz, arrayPositions, arrayHeroCards, arrayTableCards, summaTotalPot, arrayButtons, arrayControls)
            f = open("./json/"+str(ticks)+".json", mode='a', encoding='utf-8')
            f.write(json.dumps(jsonInfo) )
            f.close()
            outFileName = "./out/"+str(ticks)+".png"
            cv2.imwrite(outFileName, image)
    else:
        print("No GAME")
    indexCycle = indexCycle + 1

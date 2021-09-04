from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
import json
import time
import sys
from os import walk
import os
from time import gmtime, strftime
import preflop
main_text = None
index = 1
yLine1 = 0
yLine2 = 0
yLine3 = 0
yLine4 = 0
window = None
totalPotLabel = None
heroCardsLabel = None
tableCardsLabel = None
labelStage = None
labelOutMove = None
player1Label = None
player2Label = None
player3Label = None
player4Label = None
player5Label = None
player6Label = None
imageScreen = None
table = None
jsonFolder = "./json/"
game = {}
flagIsBusy = False
def application():
    global main_text, window, yLine1, yLine2, yLine3, yLine4
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Управление игрой")
    window.setGeometry(300, 150, 1400, 1000)
    showImageScreen("")
    yLine1 = 20
    ShowStage("...")
    ShowOurMove("...")
    yLine2 = yLine1 + 50
    ShowTitleCardsInHand()
    ShowContentCardsInHand("...")
    yLine3 = yLine2 + 50
    ShowTitleCardsInTable()
    ShowContentCardsInTable("...")
    yLine4 = yLine3 + 60
    ShowTitleTotalPot()
    ShowSummaTotalPot()
    CreateTable()
    ShowTable()
    showLabelPlayer(1, "")
    showLabelPlayer(2, "")
    showLabelPlayer(3, "")
    showLabelPlayer(4, "")
    showLabelPlayer(5, "")
    showLabelPlayer(6, "")
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1000)
    window.show()
    sys.exit(app.exec_())
def GetNewGameObject(idGame=""):
    return {
        "game": idGame,
        "herocards": [],
        "tablecards": [],
        "dealer":"",
        "players":[],
        "totalpot":[],
        "files":[],
        "log":[]
    }
def IsSameGame(jsonData):
    global game
    if IsHaveCards(game["herocards"], jsonData["herocards"]):
        return True
    return False
def IsHaveCards(arrayOldCards, arrayNewCards):
    countSameCards = 0
    for oldCard in arrayOldCards:
        if IsHaveCard(arrayNewCards, oldCard):
            countSameCards += 1
    return countSameCards == len(arrayOldCards)
def IsHaveCard(arrayCards, card):
    for crd in arrayCards:
        if crd["cost"] == card["cost"]:
            if crd["suit"] == card["suit"]:
                return True
    return False
def CreateGameFolder(strFolderName):
    print("CreateGameFolder:", strFolderName)
    CreateFolder('games/' + strFolderName)
    CreateFolder('games/' + strFolderName + '/in')
    CreateFolder('games/' + strFolderName + '/out')
    CreateFolder('games/' + strFolderName + '/log')
    CreateFolder('games/' + strFolderName + '/json')
def CreateFolder(strFolderName):
    try:
        os.mkdir('./' + strFolderName)
    except OSError:
        print ("Creation of the directory %s failed" % strFolderName)
    else:
        print ("Successfully created the directory %s " % strFolderName)
def MoveFile(src, dest):
    try:
        os.rename(src, dest)
    except OSError:
        print ("Error",src, dest)
def MoveFilesInGameFolder(strFileName, strFolderName):
    src = './in/'+strFileName+'.png'
    dest = './games/'+strFolderName+'/in/'+strFileName+'.png'
    MoveFile(src, dest)
    src = './out/'+strFileName+'.png'
    dest = './games/'+strFolderName+'/out/'+strFileName+'.png'
    MoveFile(src, dest)
    src = './json/'+strFileName+'.json'
    dest = './games/'+strFolderName+'/json/'+strFileName+'.json'
    MoveFile(src, dest)
def SaveGame():
    if len(game["game"]) > 0:
        f = open("./games/"+game["game"]+"/game.json", mode='w', encoding='utf-8')
        f.write(json.dumps(game) )
        f.close()
def LoadListFilesInFolder(strPathToFolder):
    _, _, filenames = next(walk(strPathToFolder))
    filenames.sort()
    return filenames
def GetNextFileInFolder():
    arrayFolderFiles = LoadListFilesInFolder(jsonFolder)
    strFileName = ''
    if len(arrayFolderFiles) > 0:
        strFileName = arrayFolderFiles[0]
    return strFileName
def CreateTable():
    global table
    table = QTableWidget(window)  
    table.setColumnCount(3)     
    table.setGeometry(0, 500, 1400, 500)
    table.setHorizontalHeaderLabels(["Время", "Действие", "Информация"])
    table.horizontalHeaderItem(0).setToolTip("Column 1 ")
    table.horizontalHeaderItem(1).setToolTip("Column 2 ")
    table.horizontalHeaderItem(2).setToolTip("Column 3 ")
    table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
    table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
    table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
def ShowTable():
    global table, game
    if game.get('log', False):
        loadTable(game["log"], table)
    table.resizeColumnsToContents()
def AddLog(strAction, strContent, strTime=None):
    global game
    if strTime == None or len(strTime) == 0:
        strTime = strftime("%H:%M:%S", gmtime())
    game["log"].append({
        "time": strTime,
        "action": strAction,
        "content": strContent
    })
def addRow(table, indexRow, str1, str2, str3):
    table.setItem(indexRow, 0, QTableWidgetItem(" " + str1 + " "))
    table.setItem(indexRow, 1, QTableWidgetItem(" " + str2 + " "))
    table.setItem(indexRow, 2, QTableWidgetItem(" " + str3 + " "))
def loadTable(arrDate, table):
    table.setRowCount(len(arrDate)) 
    index = 0
    for row in arrDate:
        addRow(table, index, row["time"], row["action"], row["content"])
        index = index +1
def AddFile(strFileName):
    global game
    game["files"].append({
        "file": strFileName
    })
def ShowStage(strStage):
    global window, yLine1, labelStage
    if labelStage == None:
        labelStage = QtWidgets.QLabel(window)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        labelStage.setFont(font)
        labelStage.setStyleSheet("font-weight: bold; color: red; font-Size: 120%;")
    labelStage.setText(strStage)
    labelStage.move(10, yLine1)
    labelStage.adjustSize()
def ShowOurMove(strOurMove):
    global window, yLine1, labelOutMove
    if labelOutMove == None:
        labelOutMove = QtWidgets.QLabel(window)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        labelOutMove.setFont(font)
        labelOutMove.setStyleSheet("font-weight: bold;")
    labelOutMove.setText(strOurMove)
    labelOutMove.move(250, yLine1)
    labelOutMove.adjustSize()
def ShowTitleCardsInTable():
    global window, yLine3
    labelCardsInTable = QtWidgets.QLabel(window)
    labelCardsInTable.setText("Карты на столе:")
    labelCardsInTable.move(10, yLine3)
    font = QtGui.QFont("Times", 12, QtGui.QFont.Normal)
    labelCardsInTable.setFont(font)
    labelCardsInTable.adjustSize()
def ShowContentCardsInTable(strCards):
    global window, yLine3, tableCardsLabel
    if tableCardsLabel == None:
        tableCardsLabel = QtWidgets.QLabel(window)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        tableCardsLabel.setFont(font)
    tableCardsLabel.setText(strCards)
    tableCardsLabel.move(250, yLine3)
    tableCardsLabel.adjustSize()
def ShowTitleCardsInHand():
    global window, yLine2
    stageLabel = QtWidgets.QLabel(window)
    stageLabel.setText("Карты в руке:")
    stageLabel.move(10, yLine2)
    font = QtGui.QFont("Times", 12, QtGui.QFont.Normal)
    stageLabel.setFont(font)
    stageLabel.adjustSize()
def ShowContentCardsInHand(strCards):
    global window, yLine2, heroCardsLabel
    if heroCardsLabel == None:
        heroCardsLabel = QtWidgets.QLabel(window)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        heroCardsLabel.setFont(font)
    heroCardsLabel.setText(strCards)
    heroCardsLabel.move(250, yLine2)
    heroCardsLabel.adjustSize()
def ShowTitleTotalPot():
    global window, yLine4
    stageLabel = QtWidgets.QLabel(window)
    stageLabel.setText("Общий банк:")
    stageLabel.move(10, yLine4)
    font = QtGui.QFont("Times", 12, QtGui.QFont.Normal)
    stageLabel.setFont(font)
    stageLabel.adjustSize()
def ShowSummaTotalPot():
    global game, window, yLine4, totalPotLabel
    if totalPotLabel == None:
        totalPotLabel = QtWidgets.QLabel(window)
        totalPotLabel.move(250, yLine4)
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        totalPotLabel.setFont(font)
    totalPotCahnges = GetAllTotalPotChanges()
    if len(totalPotCahnges) > 0:
        totalPotCahnges += " BB"
    totalPotLabel.setText(totalPotCahnges)    
    totalPotLabel.adjustSize()
def ShowPlayers(): 
    global game
    index = 1
    for player in game["players"]:
        strPosition = "[---]"
        if player["isHaveCards"]:
            strPosition = "[" + player["position"] + "]"
        playerName = player["name"]
        strPlayer = makeTextPlayer(strPosition, playerName, GetSummaPlayer(index-1))
        showLabelPlayer(index, strPlayer)
        index = index + 1
def makeTextPlayer(position, name, stack):
    str = ''   
    str = str + '  ' + position
    str = str + '  ' + name
    str = str + '  ' + stack
    return str
def showLabelPlayer(nomer, str):
    if nomer == 1:
        showLabelPlayer1(str)
    elif nomer == 2:
        showLabelPlayer2(str)
    elif nomer == 3:
        showLabelPlayer3(str)
    elif nomer == 4:
        showLabelPlayer4(str)
    elif nomer == 5:
        showLabelPlayer5(str)
    elif nomer == 6:
        showLabelPlayer6(str)
def showLabelPlayer1(str):
    global window, player1Label
    yLinePlayer1 = 0 * 40 + 250
    if player1Label == None:
        player1Label = QtWidgets.QLabel(window)
        player1Label.move(10, yLinePlayer1)
        player1Label.setFont(getFontNormal())
    player1Label.setText(str)
    player1Label.adjustSize()
def showLabelPlayer2(str):
    global window, player2Label
    yLinePlayer2 = 1 * 40 + 250
    if player2Label == None:
        player2Label = QtWidgets.QLabel(window)
        player2Label.move(10, yLinePlayer2)
        player2Label.setFont(getFontNormal())
    player2Label.setText(str)
    player2Label.adjustSize()
def showLabelPlayer3(str):
    global window, player3Label
    yLinePlayer3 = 2 * 40 + 250
    if player3Label == None:
        player3Label = QtWidgets.QLabel(window)
        player3Label.move(10, yLinePlayer3)
        player3Label.setFont(getFontNormal())
    player3Label.setText(str)
    player3Label.adjustSize()
def showLabelPlayer4(str):
    global window, player4Label
    yLinePlayer4 = 3 * 40 + 250
    if player4Label == None:
        player4Label = QtWidgets.QLabel(window)
        player4Label.move(10, yLinePlayer4)
        player4Label.setFont(getFontNormal())
    player4Label.setText(str)
    player4Label.adjustSize()
def showLabelPlayer5(str):
    global window, player5Label
    yLinePlayer5 = 4 * 40 + 250
    if player5Label == None:
        player5Label = QtWidgets.QLabel(window)
        player5Label.move(10, yLinePlayer5)
        player5Label.setFont(getFontNormal())
    player5Label.setText(str)
    player5Label.adjustSize()
def showLabelPlayer6(str):
    global window, player6Label
    yLinePlayer6 = 5 * 40 + 250
    if player6Label == None:
        player6Label = QtWidgets.QLabel(window)
        player6Label.move(10, yLinePlayer6)
        player6Label.setFont(getFontNormal())
    player6Label.setText(str)
    player6Label.adjustSize()
def showImageScreen(str):
    global window, imageScreen
    if imageScreen == None:
        imageScreen = QtWidgets.QLabel(window)
        imageScreen.setGeometry(660, 0, 850, 500)
    if len(str) > 0:
        pixmap1 = QtGui.QPixmap(str)
        pixmap2 = pixmap1.scaled(850, 500, QtCore.Qt.KeepAspectRatio)
        imageScreen.setPixmap(pixmap2)
def getFontNormal():
    return QtGui.QFont("Times", 12, QtGui.QFont.Normal)
def getStrCards(arrayCards):
    strCards = ''
    for card in arrayCards:
        strCards = strCards + " [" + card['cost'] + card['suit'] + "]"
    return strCards.strip()
def getStage(arrayCardInHand, arrayCardsOnTable):
    if len(arrayCardInHand) == 2 and len(arrayCardsOnTable) == 0:
        return "PREFLOP"
    if len(arrayCardInHand) == 2 and len(arrayCardsOnTable) == 3:
        return "FLOP"
    if len(arrayCardInHand) == 2 and len(arrayCardsOnTable) == 4:
        return "TERN"
    if len(arrayCardInHand) == 2 and len(arrayCardsOnTable) == 5:
        return "RIVER"
    return "..."
def getIsOurMove(arrayRedButtons, arrayControls):
    if len(arrayRedButtons) > 1 or len(arrayControls) > 1:
        return True
    return False
def getStrOurMove(arrayRedButtons, arrayControls):
    if getIsOurMove(arrayRedButtons, arrayControls):
        return "НАШ ХОД"
    return ""
def GetJsonContentFromFile(strJsonPathFileName, defaultJson):
    data = defaultJson
    try:
        with open(strJsonPathFileName) as json_file:
            data = json.load(json_file)
    except OSError:
        print("Error: ", strJsonPathFileName)
    return data
def AddSummaTotalPot(summa):
    global game
    lastSummaTotalPot = ''
    if len(game["totalpot"]) > 0:
        lastSummaTotalPot = game["totalpot"][len(game["totalpot"]) - 1]
    if not summa == '0':
        if not lastSummaTotalPot == summa:
            game["totalpot"].append(summa)
def GetAllTotalPotChanges():
    global game    
    firstSummaTotalPot = ''
    if len(game["totalpot"]) > 0:
        firstSummaTotalPot = game["totalpot"][0]
    index = 0
    strAllTotalPot = '' + firstSummaTotalPot
    for summa in game["totalpot"]:
        if index > 0:
            strAllTotalPot += "  " + summa
        index += 1
    return strAllTotalPot
def GetIndexPlayer(playerName):
    global game
    indexPlayer = -1
    index = 0
    for player in game["players"]:
        if player["name"] == playerName:
            indexPlayer = index
        index += 1
    return indexPlayer
def AddSummaToPlayer(player, indexPlayer):
    global game
    lastSummaPlayer = 0
    if len(game["players"]) > indexPlayer:
        if len(game["players"][indexPlayer]["stack"]) > 0:
            lastSummaPlayer = game["players"][indexPlayer]["stack"][len(game["players"][indexPlayer]["stack"]) - 1]
        if lastSummaPlayer != player["stack"]:
            game["players"][indexPlayer]["stack"].append(player["stack"])
    else:
        game["players"].append({
            "name": player["name"],
            "stack": [player["stack"]],
            "position": player["position"],
            "isHaveCards": player["isHaveCards"]
        })
    game["players"][indexPlayer]["isHaveCards"] = player["isHaveCards"]
def getNumberValue(s):
    ret = 0
    try:
        ret = int(s)
    except ValueError:
        try:
            ret = float(s)
        except ValueError:
            ret = 0
    return ret
def GetSummaPlayer(indexPlayer):
    global game
    startSumma = 0
    if indexPlayer > -1:
        index = 0
        predSumma = 0
        totalWaste = 0
        for summa in game["players"][indexPlayer]["stack"]:
            numValue = getNumberValue(summa)
            if index == 0:
                startSumma = numValue                
            elif numValue > 0:
                if predSumma > numValue:
                    totalWaste += (predSumma - numValue)
                    predSumma = numValue
            index += 1
    strOut = ''
    if startSumma > 0:
        strOut += str(startSumma) + " BB"
    if totalWaste > 0:
        strOut += " (" + str(totalWaste) + " BB)"
    return strOut.strip()
def StartApp():
    global jsonFolder, game
    CreateFolder('games')
    _, arrayGamesFolders, _ = next(os.walk('./games/'))
    strLastGameFolder = ""
    if len(arrayGamesFolders) > 0:
        strLastGameFolder = arrayGamesFolders[len(arrayGamesFolders) - 1]
    print("start:", strLastGameFolder)
    game = GetNewGameObject()
    if len(strLastGameFolder) > 0:
        try:
            game = GetJsonContentFromFile('./games/' + strLastGameFolder + '/game.json', game)
            print(game)
        except OSError:
            print("Error:", strLastGameFolder)     
def ParseFile(fileName):
    global game
    print("ParseFile", game["game"], fileName)
    data = {
        "players": [],
        "herocards": [],
        "tablecards": [],
        "totalpot": "",
        "dealer": 6
    }
    data = GetJsonContentFromFile(jsonFolder + fileName + '.json', data)
    isSameGame = IsSameGame(data)
    if isSameGame:
        print("same game")
        if len(game["game"]) == 0:
            game["game"] = fileName
            CreateGameFolder(fileName)
    else:
        print("new game")
        CreateGameFolder(fileName)
        game = GetNewGameObject(fileName)
        game["game"] = fileName
    herocards = data.get('herocards', [])
    tablecards = data.get('tablecards', [])
    redbuttons = data.get('redbuttons', [])
    controls = data.get('controls', [])
    stage = getStage(data['herocards'], data['tablecards'])
    ShowStage(stage)
    ShowOurMove(getStrOurMove(redbuttons, controls))
    game['herocards'] = herocards
    heroCards = getStrCards(herocards)
    ShowContentCardsInHand(heroCards)
    game['tablecards'] = tablecards
    tableCards = getStrCards(tablecards)
    ShowContentCardsInTable(tableCards)
    AddSummaTotalPot(data['totalpot'])
    ShowSummaTotalPot()
    players = data.get('players', [])
    index = 0
    for player in players:
        AddSummaToPlayer(player, index)
        index += 1
    ShowPlayers()
    AddLog("РАСПОЗНАВАНИЕ", "Скриншот - " + fileName + '.png')
    strPosition = game["players"][0]["position"]
    if stage == 'PREFLOP':
        decision = preflop.getPreflopDeсision(strPosition.lower(), game["herocards"]).upper()
        strCards = game["herocards"][0]["cost"]+game["herocards"][0]["suit"] + ', '
        strCards += game["herocards"][1]["cost"]+game["herocards"][1]["suit"]
        AddLog("РЕШЕНИЕ", stage + " - [" + strPosition.upper() + "] (" + strCards + ") = " + decision)
        AddLog("КОМАНДА", "Нажать на кнопку " + decision)
        AddLog("ИСПОЛНЕНИЕ", "Эмуляция нажатия кнопки " + decision)
    if stage == 'FLOP':
        decision = "..."
        strCombinations = preflop.getCombinations(game["herocards"], game["tablecards"])
        AddLog("РЕШЕНИЕ", "Найдены комбинации: " + strCombinations)
        AddLog("РЕШЕНИЕ", stage + " - ??? ")
        AddLog("КОМАНДА", "Нажать на кнопку " + decision)
        AddLog("ИСПОЛНЕНИЕ", "Эмуляция нажатия кнопки " + decision)
    ShowTable()
    if len(game["game"]) > 0:
        MoveFilesInGameFolder(fileName, game["game"])    
    SaveGame()
    showImageScreen("./games/" + game["game"] + "/out/" + fileName + ".png")
def RemoveExtension(strFileName):
    return strFileName[0:-5]    
def update():    
    global main_text, index, flagIsBusy
    index = index + 1
    if flagIsBusy == False:
        flagIsBusy = True
        strNameNextFile = GetNextFileInFolder()    
        if len(strNameNextFile) > 0:
            print("update"+str(index), strNameNextFile)
            strNameNextFile = RemoveExtension(strNameNextFile)
            ParseFile(strNameNextFile)
        flagIsBusy = False
if __name__ == "__main__":
    StartApp()
    application()

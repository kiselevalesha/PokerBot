
jsonPreflop = {
    "utg": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs AJ ATs",
            "KQ KQs KJs"
            ],
        "bet3call":["QQ JJ TT AQs AQ KQs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    },
    "mp": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs AJ ATs AT",
            "KQ KQs KJs"
            ],
        "call":["TT 99 88 77 66 55 44 33 22", "AQs AQ AJs KQs"],
        "bet3":["AA KK QQ JJ AKs AK"],
        "bet3call":["QQ JJ TT AQs AQ KQs AJs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    },
    "co": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs AJ ATs AT",
            "KQ KQs KJs KJ KTs KT",
            "QJs QJ QTs",
            "JTs JT",
            "A9s A9 A8s A7s",
            "J9s T9s"
            ],
        "call":["TT 99 88 77 66 55 44 33 22", "AQs AQ AJs AJ KQs QJs JTs"],
        "bet3":["AA KK QQ JJ AKs AK"],
        "bet3call":["QQ JJ TT AQs AQ KQs AJs ATs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    },
    "bu": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs AJ ATs AT",
            "KQ KQs KJs KJ KTs KT",
            "QJs QJ QTs JTs JT",
            "A9s A9 A8s A7s A6s A5s A4s A3s A2s",
            "A9 A8 A7 A6 A5",
            "K9s Q9s J9s T9s T8s",
            "98s 87s 76s 65s 54s 43s 32s",
            "98 87"
            ],
        "call":["TT 99 88 77 66 55 44 33 22", "AJs AJ KQs QJs JTs"],
        "bet3":["AA KK QQ JJ AKs AK AQs AQ"],
        "bet3call":["QQ JJ TT AQs AQ KQs AJs ATs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    },
    "sb": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs AJ ATs AT",
            "KQ KQs KJs KJ KTs KT",
            "QJs QJ QTs JTs JT",
            "A9s A9 A8s A7s A6s A5s A4s A3s A2s",
            "A9 A8 A7 A6 A5",
            "T9s",
            "98s 87s 76s 65s 54s 43s 32s"
            ],
        "call":["TT 99 88 77 66 55 44 33 22", "AQs AQ AJs AJ KQs KQ"],
        "bet3":["AA KK QQ AKs AK"],
        "bet3call":["QQ JJ TT AQs AQ KQs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    },
    "bb": {
        "raise":[
            "AA KK QQ JJ TT 99 88 77 66 55 44 33 22",
            "AKs AK AQs AQ AJs ATs",
            "KQ KQs QJs QJ JTs JT",
            "98s 87s 76s 65s 54s 43s 32s",
            "98 87"
            ],
        "call":["TT 99 88 77 66 55 44 33 22", "AQs AQ AJs AJ KQs KQ"],
        "bet3":["AA KK QQ AKs AK"],
        "bet3call":["QQ JJ TT AQs AQ KQs"],
        "bet4":["AA KK AKs AK"],
        "allin":["AA KK AKs AK"]
    }
}


def getPreflopDeсision(position, arrayCards):
    global jsonPreflop
    if len(position) > 0:
        strategy = jsonPreflop.get(position, None)
        if strategy != None:
            raize = lookingforStrategy(strategy, "raise", arrayCards)
            if raize != None:
                return "Raise"
            call = lookingforStrategy(strategy, "call", arrayCards)
            if call != None:
                return "Call"
            bet3 = lookingforStrategy(strategy, "bet3", arrayCards)
            if bet3 != None:
                return "3Bet"
            bet3call = lookingforStrategy(strategy, "bet3call", arrayCards)
            if bet3call != None:
                return "3Bet call"
            bet4 = lookingforStrategy(strategy, "bet4", arrayCards)
            if bet4 != None:
                return "4 Bet"
            allin = lookingforStrategy(strategy, "allin", arrayCards)
            if allin != None:
                return "All-in"
    return "Fold"

def lookingforStrategy(strategy, property, arrayCards):
    subStrategy = strategy.get(property, None)
    if subStrategy != None:
        for item in subStrategy:
            arrayCosts = item.split()
            for setCosts in arrayCosts:
                char1 = setCosts[0:1]
                char2 = setCosts[1:2]
                char3 = setCosts[2:3]
                if char3 == 's':
                    if arrayCards[0]["suit"] == arrayCards[1]["suit"]:
                        if isSameCosts(char1, char2, arrayCards[0]["cost"], arrayCards[1]["cost"]):
                            return property
                else:
                    if isSameCosts(char1, char2, arrayCards[0]["cost"], arrayCards[1]["cost"]):
                        return property
    return None

def isSameCosts(cost1a, cost2a, cost1b, cost2b):
    #print("isSamecosts",cost1a,cost2a,cost1b,cost2b)
    if cost1a == cost1b and cost2a == cost2b:
        return True
    if cost1a == cost2b and cost2a == cost1b:
        return True
    return False


def combineAllCards(arrayHeroCards, arrayTableCards):
    arrayCards = []
    for card in arrayHeroCards:
        arrayCards.append({
            "cost": card["cost"],
            "suit": card["suit"],
            "isHandCard": True
        })
    for card in arrayTableCards:
        arrayCards.append({
            "cost": card["cost"],
            "suit": card["suit"],
            "isHandCard": False
        })
    return arrayCards

def getAllJsonCosts():
    arrayCosts = []
    arrayCosts.append({ "cost": "2", "count": 0 })
    arrayCosts.append({ "cost": "3", "count": 0 })
    arrayCosts.append({ "cost": "4", "count": 0 })
    arrayCosts.append({ "cost": "5", "count": 0 })
    arrayCosts.append({ "cost": "6", "count": 0 })
    arrayCosts.append({ "cost": "7", "count": 0 })
    arrayCosts.append({ "cost": "8", "count": 0 })
    arrayCosts.append({ "cost": "9", "count": 0 })
    arrayCosts.append({ "cost": "T", "count": 0 })
    arrayCosts.append({ "cost": "J", "count": 0 })
    arrayCosts.append({ "cost": "Q", "count": 0 })
    arrayCosts.append({ "cost": "K", "count": 0 })
    arrayCosts.append({ "cost": "A", "count": 0 })
    return arrayCosts

def getAllJsonSuits():
    arraySuits = []
    arraySuits.append({ "suit": "d", "count": 0 })
    arraySuits.append({ "suit": "h", "count": 0 })
    arraySuits.append({ "suit": "c", "count": 0 })
    arraySuits.append({ "suit": "s", "count": 0 })
    return arraySuits

def getCountSameByCost(arrayCosts, arrayCards):
    for cost in arrayCosts:
        count = 0
        countInHand = 0
        for card in arrayCards:
            if card["cost"] == cost["cost"]:
                count += 1
                if card["isHandCard"] == True:
                    countInHand += 1
        if countInHand > 0:
            cost["count"] = count
    return arrayCosts

def getCountSameBySuit(arraySuits, arrayCards):
    for cost in arraySuits:
        count = 0
        countInHand = 0
        for card in arrayCards:
            if card["suit"] == cost["suit"]:
                count += 1
                if card["isHandCard"] == True:
                    countInHand += 1
        if countInHand > 0:
            cost["count"] = count
    return arraySuits

def getCostValue(strValue):
    arrayStrValue = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
    arrayNumValue = [2,3,4,5,6,7,8,9,10,11,12,13]
    index = 0
    for strAValue in arrayStrValue:
        if strValue == strAValue:
            return arrayNumValue[index]
        index += 1
    return 0

def sortArrayCards(arrayCards):
    flag = True
    while (flag):
        index = 0
        flag = False
        for card in arrayCards:
            if index > 0:
                card1 = arrayCards[index - 1]
                card2 = arrayCards[index]
                if getCostValue(card2["cost"]) > getCostValue(card1["cost"]):
                    card3 = card1
                    arrayCards[index - 1] = card2
                    arrayCards[index] = card3
                    flag = True
    return arrayCards

def getMaxSequenceCards(arrayCards):
    countSequence = 0
    firstCardCost = ''
    countMaxSequence = 0
    firstMaxCardCost = ''
    
    index = 0
    for card in arrayCards:
        if index > 0:
            card1 = arrayCards[index - 1]
            card2 = arrayCards[index]
            if getCostValue(card2["cost"]) == getCostValue(card1["cost"]) + 1:
                if countSequence == 0:
                    firstCardCost = getCostValue(card1["cost"])
                countSequence += 1
                if countSequence > countMaxSequence:
                    countMaxSequence = countSequence
                    firstMaxCardCost = firstCardCost
            else:
                countSequence = 0
                firstCardCost = ''
    return {
        "count": countMaxSequence,
        "startCost": firstMaxCardCost
    }

def getCombinations(arrayHeroCards, arrayTableCards):
    arrayAllCards = combineAllCards(arrayHeroCards, arrayTableCards)
    strCombination = ''

    arrayCosts = getCountSameByCost(getAllJsonCosts(), arrayCards)
    for cost in arrayCosts:
        count = cost["count"]
        if count > 0:
            strCombination += ' '
            while (count > 0):
                strCombination += cost["cost"]
                count -= 1
            
    arraySuits = getCountSameBySuit(getAllJsonSuits(), arrayCards)
    for cost in arrayCosts:
        count = cost["count"]
        if count > 0:
            strCombination += ' '
            while (count > 0):
                strCombination += cost["suit"]
                count -= 1

    arrayAllSortCards = sortArrayCards(arrayAllCards)
    jsonSequence = getMaxSequenceCards(arrayAllSortCards)
    strSequence = ''
    if jsonSequence["count"] > 4:
        strSequence = 'Street'
        if jsonSequence["startCost"] > 12:
            strSequence = 'Flash royal'
            
    strCombination += strSequence
    return strCombination


"""
arrayCards = [
    {
        "suit":"A"
    },
    {
        "suit":"K"
    }
]
zzz = getPreflopDeсision("utg", arrayCards)
print(zzz)
zzz = getPreflopDeсision("mp", arrayCards)
print(zzz)
zzz = getPreflopDeсision("co", arrayCards)
print(zzz)
zzz = getPreflopDeсision("bu", arrayCards)
print(zzz)
zzz = getPreflopDeсision("sb", arrayCards)
print(zzz)
zzz = getPreflopDeсision("bb", arrayCards)
print(zzz)

txt = "welcome to the jungle"
x = txt.split()
print(x)
"""
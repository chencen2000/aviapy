import numpy as np
import scipy.stats as stats
import math
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import argparse

def getNick(filename = 'test.json', Nick_w = 1, surface = 'AA'):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Nick" and (data["defects"][i]["surface"]) == surface:
                defectsEnergy = defectsEnergy + Nick_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getDent(filename = 'test.json', Dent_w = 1, surface = 'AA'):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Dent" and (data["defects"][i]["surface"]) == surface:
                defectsEnergy = defectsEnergy + Dent_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getScratch(filename = 'test.json', Scratch_w = 1, surface = 'AA'):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Scratch" and (data["defects"][i]["surface"]) == surface:
                defectsEnergy = defectsEnergy + Scratch_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getDiscoloration(filename = 'test.json', Discoloration_w = 1, surface = 'AA'):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Discoloration" and (data["defects"][i]["surface"]) == surface:
                defectsEnergy = defectsEnergy + Discoloration_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy


def getTotalDefectsNumber(filename = 'test.json'):
    with open(filename) as f:
        data = json.load(f)
    return len(data["defects"])

def getDefectsNumber(filename = 'test.json', surface = 'AA'):
    with open(filename) as f:
        data = json.load(f)
        defectsNumber = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["surface"]) == surface:
                defectsNumber = defectsNumber + 1
        f.close()
    return defectsNumber

def hasCrack(filename = 'test.json'):
    with open(filename) as f:
        data = json.load(f)
        isCrack = False
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Crack":
                isCrack = True
    return isCrack

def runTesting(filename, modelName):
    # load the model from disk
    loaded_model = pickle.load(open(modelName, 'rb'))

    # read in .json file
    if not os.path.isfile(filename):
        print("Error: can't find the file." + filename)

    # generate testing feature vector
    GradesProb = []
    test_x = []

    # generate test features
    defectsNumber = getTotalDefectsNumber(filename)
    dentAA = getDent(filename, 1, 'AA')
    scratchAA = getScratch(filename, 1, 'AA')
    discolorAA = getDiscoloration(filename, 2, 'AA')
    nickAA = getNick(filename, 1, 'AA')
    dentA = getDent(filename, 1, 'A')
    scratchA = getScratch(filename, 1, 'A')
    discolorA = getDiscoloration(filename, 2, 'A')
    nickA = getNick(filename, 1, 'A')
    dentB = getDent(filename, 1, 'B')
    scratchB = getScratch(filename, 1, 'B')
    discolorB = getDiscoloration(filename, 2, 'B')
    nickB = getNick(filename, 1, 'B')
    dentC = getDent(filename, 1, 'C')
    scratchC = getScratch(filename, 1, 'C')
    discolorC = getDiscoloration(filename, 2, 'C')
    nickC = getNick(filename, 1, 'C')
    NoAA = getDefectsNumber(filename, 'AA')
    totalDefectsArea = sum([dentAA, scratchAA, discolorAA, nickAA, dentA, scratchA, discolorA, nickA, \
                        dentB, scratchB, discolorB, nickB, dentC, scratchC, discolorC, nickC])

    # generate feature vector
    test_x.append([dentAA, scratchAA, discolorAA, nickAA, dentA, scratchA, discolorA, nickA, \
               dentB, scratchB, discolorB, nickB, dentC, scratchC, discolorC, nickC, \
               NoAA, defectsNumber])

    # Verizon grade
    computedGradeIndex = loaded_model.predict(test_x)
    computedProb = loaded_model.predict_proba(test_x)

    normedProb = [float(i) / sum(computedProb[0]) for i in computedProb[0]]

    # output computed grade
    ret = 'D'
    retp=None
    Grades = ['A', 'B', 'C', 'D+']
    if NoAA < 2 and discolorA < 0.01 and discolorB < 0.01:
        ret = 'A+'
    elif hasCrack(filename):
        ret = 'D'
    else:
        ret = Grades[int(computedGradeIndex)]
        retp=computedProb[0]
    return ret, retp

#Offline testing code
#print(runTesting('data_117//data117_json//345407065245010.json', 'GRRmodel'))








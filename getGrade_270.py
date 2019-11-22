import numpy as np
import scipy.stats as stats
import math
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import argparse

def getGradeProb(mu, variance, loc):
    if variance < 0:
        print("Error: variance is less than 0")
        return
    sigma = math.sqrt(variance)
    return stats.norm(mu, sigma).pdf(loc)

def getDefectsEnergy(filename = 'test.json', Scratch_w = 1, Nick_w = 1, Dent_w = 1, Discol_w = 1, Crack_w = 1):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Nick":
                defectsEnergy = defectsEnergy + Nick_w * float(data["defects"][i]["area_mm"])
            elif (data["defects"][i]["type"]) == "Dent":
                defectsEnergy = defectsEnergy + Dent_w * float(data["defects"][i]["area_mm"])
            elif (data["defects"][i]["type"]) == "Scratch":
                defectsEnergy = defectsEnergy + Scratch_w * float(data["defects"][i]["area_mm"])
            elif (data["defects"][i]["type"]) == "Discoloration":
                defectsEnergy = defectsEnergy + Discol_w * float(data["defects"][i]["area_mm"])
            elif (data["defects"][i]["type"]) == "Crack":
                defectsEnergy = defectsEnergy + Crack_w * float(data["defects"][i]["area_mm"])
        #print(len(data["defects"]))
        #print(data["defects"][0]["area_pixel"])
    return defectsEnergy

def getDefectsNumber(filename = 'test.json'):
    with open(filename) as f:
        data = json.load(f)
    return len(data["defects"])

def getNick(filename = 'test.json', Nick_w = 1):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Nick":
                defectsEnergy = defectsEnergy + Nick_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getDent(filename = 'test.json', Dent_w = 1):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Dent":
                defectsEnergy = defectsEnergy + Dent_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getScratch(filename = 'test.json', Scratch_w = 1):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Scratch":
                defectsEnergy = defectsEnergy + Scratch_w * float(data["defects"][i]["area_mm"])
        f.close()
    return defectsEnergy

def getDiscoloration(filename = 'test.json', Discoloration_w = 1):
    with open(filename) as f:
        data = json.load(f)
        defectsEnergy = 0
        for i in range(len(data["defects"])):
            if (data["defects"][i]["type"]) == "Discoloration":
                defectsEnergy = defectsEnergy + Discoloration_w * float(data["defects"][i]["value"] / 100)
        f.close()
    return defectsEnergy


def runTesting(filename, modelName):
    # load the model from disk
    loaded_model = pickle.load(open(modelName, 'rb'))

    # read in .json file
    if not os.path.isfile(filename):
        print("Error: can't find the file." + filename)

    # generate testing feature vector
    test_x = []
    defectsNumber = getDefectsNumber(filename)
    dent = getDent(filename, 1)
    scratch = getScratch(filename, 1)
    discolor = getDiscoloration(filename, 2)
    nick = getNick(filename, 1)
    test_x.append([dent, scratch, discolor, nick, defectsNumber])
    computedGradeIndex = loaded_model.predict(test_x)
    computedProb = loaded_model.predict_proba(test_x)

    # output computed grade
    Grades = ['A', 'B', 'C', 'D+']
    #print(computedProb)
    #print("Computed Grade:")
    #return Grades[int(computedGradeIndex)]
    return Grades[int(computedGradeIndex)], computedProb[0]


'''
# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
# Required positional argument
parser.add_argument('fileName', type=str, help='A required file to process')
parser.add_argument('modelName', type = str, help = 'A required model to use')
args = parser.parse_args()
filename = args.fileName
modelName = args.modelName
print(args.fileName)

# load the model from disk
loaded_model = pickle.load(open(modelName, 'rb'))

# read in .json file
if not os.path.isfile(filename):
    print("Error: can't find the file." + filename)

# generate testing feature vector
test_x = []
defectsNumber = getDefectsNumber(filename)
dent = getDent(filename, 1)
scratch = getScratch(filename, 1)
discolor = getDiscoloration(filename, 2)
nick = getNick(filename, 1)
test_x.append([dent, scratch, discolor, nick, defectsNumber])
computedGradeIndex = loaded_model.predict(test_x)
computedProb = loaded_model.predict_proba(test_x)

# output computed grade
Grades = ['A', 'B', 'C', 'D+']
#print(computedProb)
print("Computed Grade:")
print(Grades[int(computedGradeIndex)])

'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optional app description')
    # Required positional argument
    parser.add_argument('fileName', type=str, help='A required file to process')
    parser.add_argument('modelName', type = str, help = 'A required model to use')
    args = parser.parse_args()
    filename = args.fileName
    modelName = args.modelName
    print('predict {} using {}'.format(args.fileName, args.modelName))
    g, posibility = runTesting(filename, modelName)
    resp={'grade': 'D'}
    resp['grade'] = g
    resp['posibility'] = posibility.tolist()
    print(json.dumps(resp))


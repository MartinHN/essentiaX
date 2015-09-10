from utils.algorithms_info import *
import os
import sys

from openstep_parser import *


def getTarget(x):
    root = x["rootObject"]
    targets = x["objects"][root]["targets"]
    for t in targets:
            if x["objects"][t]["name"] == "essentiaX":
                print "found"
                return t;
    print "no target found"

def getBuildFiles(x,t):
    res = []
    ref = []
    for b in x["objects"][t]["buildPhases"]:
        if x["objects"][b]["isa"] == "PBXSourcesBuildPhase":
            print "found build : "+str(b)
            for hf in x["objects"][b]["files"]:
                ref+=[x["objects"][hf]["fileRef"]]

    
    for hf in ref:
        res += [x["objects"][hf]["path"] ]
    return res



def getDependencies(a,res,algos,rootDir):
    
    with open(rootDir + "/" +algos[a]["source"]) as file:
        lines = file.readlines()

    newdep = []
    for l in lines:
        for al in algos:  
            if "\""+al+"\"" in l and al != a:
                newdep+=[al]
    newdep = list(set(newdep))
    
        

    for d in newdep:
        getDependencies(d,res,algos,rootDir)
        del algos[d]
        res+=[d]
    return res;





if __name__ == '__main__':
    
  
    essentiasrc = sys.argv[1]
    xcodeFile = sys.argv[2]+"/project.pbxproj"
    with open(xcodeFile) as file:

        xcode =  OpenStepDecoder.ParseFromFile(file);

        t = getTarget(xcode)
        files = getBuildFiles(xcode, t)

    algodir = os.path.join(essentiasrc,"algorithms")    
    # create_version_h();

    algos = get_all_algorithms(algodir,essentiasrc)
    print algos
    res = []
    
    algos2 = algos.copy()
    print getDependencies("LowLevelSpectralExtractor", res, algos2, essentiasrc)






    ignore = []
    for a in algos:
        essSrc = algos[a]["source"].split("/")[-1]
        if not  essSrc in files:
            ignore+=[a]

    print "ignored : " + str(ignore)

    for i in ignore:
        del algos[i]

    regFile = os.path.join(algodir,"essentia_algorithms_reg.cpp")
    create_registration_cpp(algos,regFile)



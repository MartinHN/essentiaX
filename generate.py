from utils.algorithms_info import *
import os
import sys
import re

from openstep_parser import *


def getTarget(x,name):
    root = x["rootObject"]
    targets = x["objects"][root]["targets"]
    for t in targets:
            if x["objects"][t]["name"] == name:
                print "found"
                return t;
    print "no target found"


def getBuildRef(x,t):
    res = []
    for b in x["objects"][t]["buildPhases"]:
        if x["objects"][b]["isa"] == "PBXSourcesBuildPhase":
            res+=[b]
    return res

def getBuildFileRef(x,t):
    ref = []
    for b in x["objects"][t]["buildPhases"]:
        if x["objects"][b]["isa"] == "PBXSourcesBuildPhase":
            print "found build : "+str(b)
            for hf in x["objects"][b]["files"]:
                ref+=[x["objects"][hf]["fileRef"]]
    return ref

def getPathFromRef(x,ref):
    res = []
    for hf in ref:
        if hf in x["objects"]:
            r = hf
            if "fileRef" in x["objects"][hf]:
                r= x["objects"][hf]["fileRef"] 
            res += [x["objects"][r]["path"] ]
    return res




def getDependencies(a,res,algos,rootDir):
    # print "getDependencies for "+a
    if(not a in algos) :
        return res
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
        # del algos[d]
        res+=[d]

    del algos[a]
    return res;





def pruneXcode(xc,t,toRemove,xcodeFile):

    files =  getBuildFileRef(xc,t);
    with open(xcodeFile) as file:
        lines = file.readlines()

    inSection = False
    build = getBuildRef(xc, t)[0]

    srcToRm = [x["source"].split('/')[-1] for x in toRemove.itervalues()]

    print srcToRm


    ltodelete = []
    i = 0
    for l in lines:
        if len(l)>2:
            
            if inSection:
                if "};" in l:
                    inSection = False
                
                ref = str(re.split('\W+', l)[1])
                if ref and ref[0].isdigit():
                    curS = getPathFromRef(xc, [ref])
                    
                    if curS[0] in srcToRm:
                        ltodelete+=[i]
                        i-=1
                        print "remove : "+str(i)+" "+str(curS)
            if build  in l and l[-2]=='{':
                inSection = True
        i+=1


    for lt in ltodelete:
        # pass
        del lines[lt]

    with open(xcodeFile + "2",'w') as file:
        file.writelines(lines)
   


if __name__ == '__main__':
    
    env =  os.environ
    pruneIt = []
    
    if "ESSENTIA_PRUNE" in env:
        pruneIt = os.environ["ESSENTIA_PRUNE"].split(' ')
    print "pruning for algos : " + str(pruneIt)


    essentiasrc = sys.argv[1]
    xcodeFile = sys.argv[2]+"/project.pbxproj"
    target = sys.argv[3]


    with open(xcodeFile) as file:
        xcode =  OpenStepDecoder.ParseFromFile(file);

        t = getTarget(xcode,target)
        files = getPathFromRef(xcode,getBuildFileRef(xcode, t))


    algodir = os.path.join(essentiasrc,"algorithms")    
    # create_version_h();

    algos = get_all_algorithms(algodir,essentiasrc)
    print algos
    res = []
    print files




    ignore = []
    for a in algos:
        essSrc = algos[a]["source"].split("/")[-1]
        if not  essSrc in files:
            ignore+=[a]

    print "ignored : " + str(ignore)

    for i in ignore:
        del algos[i]


    if pruneIt:
        toRemove = algos.copy()
        for a in pruneIt:
            getDependencies(a, res, toRemove, essentiasrc)
            
        
        if"FFTA" in toRemove:
            del toRemove["IFFTA"]
            del toRemove["FFTA"]

        
        
        # pruneXcode(xcode, getTarget(xcode,"essentiaXLight"),toRemove,xcodeFile)
        rstr = []
        for r in toRemove:
            rstr+=[r]
        print "you can remove "+ str(rstr)
        

    regFile = os.path.join(algodir,"essentia_algorithms_reg.cpp")
    create_registration_cpp(algos,regFile)



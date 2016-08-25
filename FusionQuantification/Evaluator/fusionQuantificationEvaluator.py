#! /usr/bin/env python

import sys
import os
import math
import getopt
import warnings
from scipy import stats

def usage():
    print """
    fusionQuantitationEvaluator -t <truth-file> -i <input-bedpe>
    
    Requested Parameters:
        -t/--truth-file         [string:    path to truth file ]
        -i/--input-file         [string:    path to input bedpe]

    Version:                    1.0.0
          """


#parameters
inTruthFile= ''              #input truth
inResFile = ''               #input bedpe

def getParameters(argv):
    try:
        opts, args = getopt.getopt(argv,"ht:i:",["help",
                                                     "truth-file=",
                                                     "input-file="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit(0)
        elif opt in ("-i", "--input-file"):
            global inResFile
            inResFile= arg
        elif opt in ("-t","--truth-file"):
            global inTruthFile
            inTruthFile = arg


def string_to_value(message):
    userInput = float(message)
    return userInput

def is_same(truth,res):
    if truth[0]!=res[0] or truth[3]!=res[3] or truth[8]!=res[8] or truth[9]!=res[9]:
        return False
    else:
        tpos1=0
        tpos2=0
        if truth[8]=="+":
            tpos1=int(truth[2])
        else:
            tpos1=int(truth[1])
        if truth[9]=="+":
            tpos2=int(truth[4])
        else:
            tpos2=int(truth[5])
                
        rpos1=0
        rpos2=0
        if res[8]=="+":
            rpos1=int(res[2])
        else:
            rpos1=int(res[1])
        if res[9]=="+":
            rpos2=int(res[4])
        else:
            rpos2=int(res[5])
                
        delta1=0
        delta2=0
        if truth[8]=="+":
            delta1 = tpos1-rpos1
        else:
            delta1 = rpos1-tpos1
        if truth[9]=="+":
            delta2 = tpos2-rpos2
        else:
            delta2 = rpos2-tpos2
        if delta1 == delta2:
            return True
    return False

truth_bedpe = []

def load_truth(fileName):
    infile = "%s" % fileName
    f=open(infile,"r")
    index=0
    while True:
        line=f.readline()
        if line=="":
            break
        else:
            tmp=line.split("\t")
            truth_bedpe.append(tmp)
    f.close()

res_bedpe = []

def load_res(fileName):
    infile = "%s" % fileName
    f=open(infile,"r")
    index=0
    while True:
        line=f.readline()
        if line=="":
            break
        else:
            tmp=line.split("\t")
            res_bedpe.append(tmp)
    f.close()

res_quantity = []

def initial_res_quantity():
    for x in range(len(truth_bedpe)):
        res_quantity.append(0);

def get_res_quantity():
    for x in range(len(truth_bedpe)):
        for y in range(len(res_bedpe)):
            if is_same(truth_bedpe[x],res_bedpe[y]):
                res_quantity[x]=string_to_value(res_bedpe[y][10])
                continue

truth_values = []

def get_truth_values():
    for x in range(len(truth_bedpe)):
        truth_values.append(string_to_value(truth_bedpe[x][10]))


def calculateCor():
    print truth_values,res_quantity
    cor,p_value=stats.spearmanr(truth_values,res_quantity)
    final = "spearman\tp-value\n%s\t%s" % (cor,p_value)
    print(final)
    return(final)

def main(argv):
    getParameters(argv[1:])
    if inTruthFile=='' or inResFile=='':
        usage()
        return 1    
    load_truth(inTruthFile)
    load_res(inResFile)
    initial_res_quantity()
    get_res_quantity()
    get_truth_values()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        final = calculateCor()
        with open("quantification_result.out",'w') as results:
            results.write(final)
            results.close()
    return(0)

if __name__ == '__main__':
    sys.exit(main(sys.argv)) 

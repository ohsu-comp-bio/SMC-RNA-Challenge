#! /usr/bin/env python

import sys
import os
import math
import getopt
from collections import Counter 
from collections import defaultdict

def usage():
    print """
    quantificationValidator -g <gene-model-gtf>  -i <input-tsv>
    
    Requested Parameters:
        -g/--gene-model-gtf    [string:    path to gene model gtf ]
        -i/--input-tsv         [string:    path to input tsv      ]

    Version:                    1.0.0
          """


#parameters
inFile = ''               #input tsv
geneModel = ''           #gene model gtf

def getParameters(argv):
    try:
        opts, args = getopt.getopt(argv,"hg:i:",["help",
                                                 "gene-model-gtf=",
                                                 "input-tsv="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit(1)
        elif opt in ("-i", "--input-tsv"):
            global inFile
            inFile= arg
        elif opt in ("-g","--gene-model-gtf"):
            global geneModel
            geneModel = arg



transcripts_in_model = defaultdict(lambda: 'badTranscriptName')

def getAllTranscriptNames():
    infile = "%s" % geneModel
    f=open(infile,"r")
    while True:
        line=f.readline()
        if line=="":
            break
        #GTF files have comments
        elif line.startsWith("#"):
            continue
        else:
            tmp=line.split("\t")
            tmp2=tmp[8].split(" ")
            tmp3=tmp2[3].split(";")
            tmp4=tmp3[0]
            name = tmp4.replace("\"","")
            transcripts_in_model[name]='transcript'

def isFloat(message):
    try:
        userInput = float(message)
    except ValueError:
        message=message[0:len(message)-1]
        print "The value \""+message+"\"" " is not number."
        sys.exit(1)
    return True

transcripts_used = defaultdict(lambda: 0)

def valideRecord():
    infile = "%s" % inFile
    f=open(infile,"r")
    #ignore all headers
    while True:
        line=f.readline()
        if line=="":
            break
        elif not line.startsWith("ENST"):
            continue
        else:
            tmp=line.split("\t")
            line=line[0:len(line)-1]
            if len(tmp)!=2:
                line=line[0:len(line)-1]
                print "Line with not 2 fields: >>>> ", line, " <<<<.",
                sys.exit(1)
            name=tmp[0]
            value=tmp[1]
            if transcripts_in_model[name]!='transcript':
                print "Transcript name: >>>> ",name," <<<< not from gene model."
                sys.exit(1)
            if transcripts_used[name]>0:
                print "Repeat transcript: >>>>",name," <<<<."
                sys.exit(1)
            if isFloat(value):
                transcripts_used[name]=1

def main(argv):
    getParameters(argv[1:])
    if inFile=='' or geneModel=='':
        usage()
        return 1
    getAllTranscriptNames()
    valideRecord()
    print "Validated"
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))


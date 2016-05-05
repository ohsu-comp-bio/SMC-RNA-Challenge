import sys
import os
import math
import getopt

def usage():
    print """
    bedpeValidatorS -c <chromosome-file> -i <input-bedpe>
    
    Requested Parameters:
        -c/--chromosome-file    [string:    path to chromosome file]
        -i/--input-file         [string:    path to input bedpe    ]

    Version:                    s1.0.0 (Simple Check Version)
          """


#parameters
inChrFile= ''                #input chromosome file
inResFile = ''               #input bedpe

def getParameters(argv):
    try:
        opts, args = getopt.getopt(argv,"hc:i:",["help",
                                                     "chromosome-file=",
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
        elif opt in ("-c","--chromosome-file"):
            global inChrFile
            inChrFile = arg

string_to_valid = {} #allowed chr name to target chr name

valid_to_length = {} #target chr length

def get_valid_name_length(fileName):
    infile = "%s" % fileName
    f=open(infile,"r")
    f.readline()
    while True:
        line=f.readline()
        if line=="":
            break
        else:
            tmp=line.split("\t")
            target=tmp[0]
            length=int(tmp[1])
            allowed=tmp[2].split(",")
            if len(allowed) > 0:
                allowed[len(allowed)-1]= allowed[len(allowed)-1][0:len(allowed[len(allowed)-1])-1]
            for i in range(len(allowed)):
                if allowed[i]!='':
                    string_to_valid[allowed[i]]=target
                    valid_to_length[target]=length
    f.close()

def get_target(name):
    try:
        target=string_to_valid[name]
    except KeyError:
        print "Chromosome name \""+name+"\"" " is not allowed."
        sys.exit(1)
    return target

def get_integer(message):
    try:
        userInput = int(message)       
    except ValueError:
        print "Position \""+message+"\"" " is not an integer."
        sys.exit(1)
    return userInput 

def get_length(target):
    return valid_to_length[target]    

def valid_pos_pair(pos1,pos2,length):
    ism1_1=True
    ism1_2=True
    if(pos1!=-1):
        ism1_1=False
    if(pos2!=-1):
        ism1_2=False
    if ism1_1 and ism1_2:
        print "Positions -1 -1 are not allowed."
    if ism1_1 and (not ism1_2):
        if pos2>length or pos2<1:
            print "Position",pos2,"out of range" 
            sys.exit(1)
    if (not ism1_1) and ism1_2:
        if pos1+1>length or pos1+1<1:
            print "Position",pos1,"out of range"
            sys.exit(1)
    if (not ism1_1) and (not ism1_2):
        if pos1+1>pos2:
            print "Position",pos1,"+1 >",pos2
            sys.exit(1)
        if pos1+1<1:
             print "Position",pos1,"out of range"
        if pos2>length:
             print "Position",pos2,"out of range"

def valid_strand(strand):
    if not (strand=="+" or strand=="-" or strand=="."):
        print "Strand should only contain +/-/."
        sys.exit(1)
    return strand

def is_contain_dot(strand1,strand2):
    if strand1=="." or strand2==".":
        return True
    else:
        return False

out_data = []

def validate_file(fileName):
    infile = "%s" % fileName
    f=open(infile,"r")
    index=0
    while True:
        line=f.readline()
        if line=="":
            break
        else:
            tmp=line.split("\t")
            if(len(tmp)<10):
                print "Number of columns of bedpe for fusion should >=10."
                sys.exit(1)
            tmp[len(tmp)-1] = tmp[len(tmp)-1][0:len(tmp[len(tmp)-1])-1]
            chr1=get_target(tmp[0])
            tmp[0]=chr1
            valid_pos_pair(get_integer(tmp[1]),get_integer(tmp[2]),get_length(chr1))
            chr2=get_target(tmp[3])
            tmp[3]=chr2
            valid_pos_pair(get_integer(tmp[4]),get_integer(tmp[5]),get_length(chr2))
            iscd=is_contain_dot(valid_strand(tmp[8]),valid_strand(tmp[9]))
            if iscd==True:
                print "Dot not allowed for strand."
                sys.exit(1)
            out_data.append(tmp) 
    f.close()

def remove_duplicate():
    global out_data
    for i in range(len(out_data)):
        pos1=0
        pos2=0
        if out_data[i][8]=="+":
            pos1=out_data[i][2]
        else:
            pos1=out_data[i][1]
        if out_data[i][9]=="+":
            pos2=out_data[i][4]
        else:
            pos2=out_data[i][5]
        out_data[i].append(get_integer(pos1))
        out_data[i].append(get_integer(pos2))
        
    out_data = sorted(out_data, key = lambda x: (x[0], x[3], x[8], x[9], x[10], x[11]))
    out_data_2 = []
    for i in range(len(out_data)):
        if i==0:
            out_data_2.append(out_data[i])
        if i>=1:
            if out_data[i][0]==out_data[i-1][0] and out_data[i][3]==out_data[i-1][3] and out_data[i][8]==out_data[i-1][8] and out_data[i][9]==out_data[i-1][9]:
                delta1=0
                delta2=0
                lenRow=len(out_data[i])
                if out_data[i][8]=="+":
                    delta1 = out_data[i][lenRow-2]-out_data[i-1][lenRow-2]
                else:
                    delta1 = out_data[i-1][lenRow-2]-out_data[i][lenRow-2]
                if out_data[i][9]=="+":
                    delta2 = out_data[i][lenRow-1]-out_data[i-1][lenRow-1]
                else:
                    delta2 = out_data[i-1][lenRow-1]-out_data[i][lenRow-1]
                if delta1 ==delta2:
                    print "line :",out_data[i-1][0],out_data[i-1][1],out_data[i-1][2]," ... and line ",out_data[i][0],out_data[i][1],out_data[i][2]," ... are essentially the same"
                    sys.exit(1)

def main(argv):
    getParameters(argv[1:])
    if inChrFile=='' or inResFile=='':
        usage()
        sys.exit(1)
    
    get_valid_name_length(inChrFile)
    validate_file(inResFile)
    remove_duplicate()
    print "Validated" 

if __name__ == '__main__':
    sys.exit(main(sys.argv)) 

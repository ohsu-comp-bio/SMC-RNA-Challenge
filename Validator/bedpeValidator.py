import sys
import os
import math
import getopt

def usage():
    print """
    bedpeValidator -c <chromosome-file> -i <input-bedpe> -o <output-bedpe>
    
    Requested Parameters:
        -c/--chromosome-file    [string:    path to chromosome file]
        -i/--input-file         [string:    path to input bedpe    ]
        -o/--output-file        [string:    path to output bedpe   ]

    Optional Parameters:
        -s/--is-strict          [Change to True. Default: False  No user strings                       ]
        -d/--is-keep-dot        [Change to True. Default: False  Not keeping lines with strands as dots]
          """


#parameters
inChrFile= ''                #input chromosome file
inResFile = ''               #input bedpe
outResFile = ''              #output bedpe
isStrict = False             #If True, {only keeps column 1-6,9-10;7,8 will assign values by this code}
                             #If False, only check 1-6,9-10
isKeepDotInStrand = False    #If True, keeps the records with dots in strands

def getParameters(argv):
    try:
        opts, args = getopt.getopt(argv,"hc:i:o:sd",["help",
                                                     "chromosome-file=",
                                                     "input-file=",
                                                     "output-file=",
                                                     "is-strict",
                                                     "is-keep-dot"])
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
        elif opt in ("-o", "--output-file"):
            global outResFile
            outResFile = arg
        elif opt in ("-c","--chromosome-file"):
            global inChrFile
            inChrFile = arg
        elif opt in ("-s","--is-strict"):
            global isStrict
            isStrict = True
        elif opt in ("-d","--is-keep-dot"):
            global isKeepDotInStrand
            isKeepDotInStrand = True



string_to_valid = {} #allowed chr name to target chr name

valid_to_length = {} #target chr length

out_data = [] #keep output

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
    #for x in string_to_valid:
    #    print "%s:%s" % (x,string_to_valid[x])
    #for x in valid_to_length:
    #    print "%s:%d" % (x,valid_to_length[x])
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
                exit(1)
            tmp[len(tmp)-1] = tmp[len(tmp)-1][0:len(tmp[len(tmp)-1])-1]
            chr1=get_target(tmp[0])
            tmp[0]=chr1
            valid_pos_pair(get_integer(tmp[1]),get_integer(tmp[2]),get_length(chr1))
            chr2=get_target(tmp[3])
            tmp[3]=chr2
            valid_pos_pair(get_integer(tmp[4]),get_integer(tmp[5]),get_length(chr2))
            iscd=is_contain_dot(valid_strand(tmp[8]),valid_strand(tmp[9]))
            if isKeepDotInStrand==False and iscd==True:
                continue
            else:
                if isStrict:
                    tmp[6]="name"+str(index)
                    tmp[7]="0"
                    tmp2=[]
                    for x in range(10):
                        tmp2.append(tmp[x])
                    out_data.append(tmp2)
                else:
                    out_data.append(tmp) 
                index=index+1
    f.close()

def print_to_file(fileName):

    outfile = "%s" % fileName
    f=open(outfile,"w")
    for i in range(len(out_data)):
        tmp=out_data[i]
        for j in range(len(tmp)-1):
            f.write(tmp[j])
            f.write("\t")
        f.write(tmp[len(tmp)-1])
        f.write("\n") 
    f.close()    


if __name__ == '__main__':
    getParameters(sys.argv[1:])
    if inChrFile=='' or inResFile=='' or outResFile=='':
        usage()
        sys.exit(0)
	
    #print "inResFile:\t", inResFile
    #print "outResFile:\t", outResFile
    #print "inChrFile:\t", inChrFile
    #print "isStrict:\t", isStrict
    #print "sKeepDotInStrand:\t", isKeepDotInStrand


    get_valid_name_length(inChrFile)
    
    validate_file(inResFile)

    print_to_file(outResFile) 

#include "Bedpe.h"


int Bedpe::loadFromFile(char * filename)
{
  bedpevec.clear();
  string line;
  bedpe_t bt;
  ifstream myfile (filename);
  if (myfile.is_open())
  {
    while ( getline (myfile,line) )
    {
        std::vector<std::string> tmp = my_split(line, '\t');
        bt.chr1=tmp[0];
        bt.start1=atol(tmp[1].c_str());
        bt.end1=atol(tmp[2].c_str());
        bt.chr2=tmp[3];
        bt.start2=atol(tmp[4].c_str());
        bt.end2=atol(tmp[5].c_str());
        bt.name=tmp[6];
        bt.score=atof(tmp[7].c_str()); 
        bt.strand1=tmp[8][0];
        bt.strand2=tmp[9][0];
        if(tmp.size()>10)
        {
            std::copy ( tmp.begin()+10, tmp.begin()+(tmp.size()-10), bt.others.begin());
        }
        bedpevec.push_back(bt);
    }
    myfile.close();
  }    

  return 0;
}

int Bedpe::getPos(bedpe_t & tt, uint32_t & tt_pos5, uint32_t & tt_pos3)
{
    if(tt.strand1.compare("+")==0)
    {
        tt_pos5=tt.end1;
    }
    else
    {
        tt_pos5=tt.start1+1;
    }

    if(tt.strand2.compare("+")==0)
    {
        tt_pos3=tt.start2+1;
    }
    else
    {
        tt_pos3=tt.end2;
    }

    return 0;
}


int Bedpe::printBedpe(char * file)
{
    
    std::ofstream ofs;
    ofs.open (file, std::ofstream::out);
    
    for(int i=0;i<bedpevec.size();i++)
    {
        bedpe_t bt=bedpevec[i];    
        ofs<<bt.chr1<<"\t";
        ofs<<bt.start1<<"\t";
        ofs<<bt.end1<<"\t";
        ofs<<bt.chr2<<"\t";
        ofs<<bt.start2<<"\t";
        ofs<<bt.end2<<"\t";
        ofs<<bt.name<<"\t";
        ofs<<bt.score<<"\t";
        ofs<<bt.strand1<<"\t";
        ofs<<bt.strand2;
        if(bt.others.size()==0)
           ofs<<"\n";
        else 
        {
           for(int j=0;j<bt.others.size()-1;j++)        
           {
               ofs<<bt.others[j]<<"\t";
           }
           ofs<<bt.others[bt.others.size()-1]<<endl;
        }
    } 
    ofs.close();

    return 0;
}



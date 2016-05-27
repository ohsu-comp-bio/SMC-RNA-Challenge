# Automation of validation and scoring
# Make sure you point to the directory where challenge.py belongs and a log directory must exist for the output
cd /home/thomas_yu/SMC-RNA-Challenge/challenge/
#---------------------
#Validate submissions
#---------------------
python challenge.py -u SMC_RNA --send-messages --acknowledge-receipt --notifications validate --all >> log/score.log 2>&1

#--------------------
#Score submissions
#--------------------
#python challenge.py -u SMC_RNA --send-messages --notifications score --all >> log/score.log 2>&1

#--------------------
#Cache submissions
#--------------------
#Fusion detection
python challenge.py -u SMC_RNA archive 5877348 syn6045218 
#Isoform Quantification
python challenge.py -u SMC_RNA archive 5952651 syn6045218 

FROM ubuntu:14.04

RUN apt-get -y update && \
	apt-get install -y git && \
	apt-get install -y python && \
	git clone https://github.com/Sage-Bionetworks/SMC-RNA-Challenge.git && \
	cp SMC-RNA-Challenge/convert_tophapt_to_bedpe.py /usr/local/bin/


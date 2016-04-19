FROM ubuntu:14.04

#Install Essentials
RUN apt-get -y update
RUN apt-get install -y git build-essential cmake gcc python

#Install converter, evaluator, validator
WORKDIR /opt
RUN git clone https://github.com/Sage-Bionetworks/SMC-RNA-Challenge.git && \
    git clone https://github.com/Sage-Bionetworks/SMC-RNA-Examples.git && \
	cd SMC-RNA-Challenge && \
	cp challenge/evaluation.py /usr/local/bin/ && \
	cp ../SMC-RNA-Examples/tophat/script/convert_tophat_to_bedpe.py /usr/local/bin/ && \
	mkdir build && \
	cd build && \
	cmake ../FusionEvaluator/ -DCMAKE_BUILD_TYPE=release && \
	make && \
	cp bin/fusionToolEvaluator /usr/local/bin/

ENV PATH /usr/local/bin/:/usr/bin:/bin

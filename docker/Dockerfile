FROM ubuntu:14.04

#Install Essentials
RUN apt-get -y update
RUN apt-get install -y git build-essential cmake gcc python python-pip python-dev python-numpy python-scipy

WORKDIR /opt

#Install evaluators, and validators
RUN git clone https://github.com/Sage-Bionetworks/SMC-RNA-Challenge.git && \
	cd SMC-RNA-Challenge && \
	mkdir build && \
	cd build && \
	cmake ../FusionDetection/Evaluator/ -DCMAKE_BUILD_TYPE=release && \
	make

ENV PATH /opt/SMC-RNA-Challenge/IsoformQuantification/Validator/:/usr/bin:/bin
ENV PATH /opt/SMC-RNA-Challenge/IsoformQuantification/Evaluator/:/usr/bin:/bin 
ENV PATH /opt/SMC-RNA-Challenge/build/bin/:/usr/bin:/bin
ENV PATH /opt/SMC-RNA-Challenge/FusionDetection/Validator/:/usr/bin:/bin
ENV PATH /opt/SMC-RNA-Challenge/script/:/usr/bin:/bin


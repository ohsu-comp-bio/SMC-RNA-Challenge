FROM ubuntu:14.04

#Install Essentials
RUN apt-get -y update
RUN apt-get install -y git build-essential cmake gcc python python-pip python-dev python-numpy python-scipy

WORKDIR /opt

#Install evaluators, and validators
RUN git clone https://github.com/Sage-Bionetworks/SMC-RNA-Challenge.git && \
	cd SMC-RNA-Challenge && \
	cp script/evaluation.py /usr/local/bin/ && \
	cp FusionDetection/Validator/bedpeValidatorS.py /usr/local/bin && \
	cp IsoformQuantification/Validator/quantificationValidator.py /usr/local/bin && \
	cp IsoformQuantification/Evaluator/quantificationEvaluator.py /usr/local/bin && \
	mkdir build && \
	cd build && \
	cmake ../FusionDetection/Evaluator/ -DCMAKE_BUILD_TYPE=release && \
	make && \
	cp bin/fusionToolEvaluator /usr/local/bin/

ENV PATH /usr/local/bin/:/usr/bin:/bin

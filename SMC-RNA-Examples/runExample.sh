#!/bin/bash
cd test_tophatCWL &&\
wget http://ccb.jhu.edu/software/tophat/downloads/test_data.tar.gz &&\
tar -zxvf test_data.tar.gz && \
cwl-runner test-workflow.cwl test-input.json
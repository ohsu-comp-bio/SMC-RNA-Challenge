class: DockerRequirement
dockerPull: thomasvyu/tophat
dockerFile: |
  FROM ubuntu:14.04

  RUN apt-get -y update && \ 
  apt-get install -y wget zip bzip2 && \
  apt-get install -y tophat && \
  apt-get install -y bowtie && \
  apt-get install -y samtools

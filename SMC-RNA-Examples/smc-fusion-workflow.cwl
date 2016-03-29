#!/usr/bin/env cwl-runner
#
# Author: thomas.yu@sagebase.org

class: SMC-RNA fusion Workflow

cwlVersion: "cwl:draft-3.dev3"

description:
  creates custom genome from reference genome and two phased VCF files SNPs and Indels

requirements:
  - $import: envvar-global.cwl

inputs: 
  - id: bowtie_index
    type: File

  - id: fastq1
    type: File

  - id: fastq2
    type: File

outputs:

  - id: output
    type: File
    source: "#converttobedpe/fusionout"

steps:

  - id: tophat
    run: tophat.cwl
    inputs:
    - {id: p, default: 5}
    - {id: r, default: 0}
    - {id: fusion-search, default: true}
    - {id: keep-fasta-order, default: true}
    - {id: bowtie1, default: true}
    - {id: mate-std-dev, default: 80}
    - {id: o, default: testwork}
    - {id: max-intron-length, default: 100000}
    - {id: fusion-min-dist, default: 100000}
    - {id: fusion-anchor-length, default: 13}
    - {id: fusion-ignore-chromosomes, default: chrM}
    #pass in the first bowtie 2 reference
    - {id: bowtie_index, source: #bowtie_index}
    - {id: fastq1, source: #fastq1}
    - {id: fastq2, source: #fastq2}
    outputs:
    - {id: tophatOut}

  - id: converttobedpe
    run: convert.cwl
    inputs:
    - {id: input, source: "#tophat/tophatOut"}
    - {id: output, default: "output.txt"}
    outputs:
    - {id: fusionout}
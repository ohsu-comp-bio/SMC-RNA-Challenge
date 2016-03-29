#!/usr/bin/env cwl-runner
#
# Author: thomas.yu@sagebase.org

class: Workflow

cwlVersion: "cwl:draft-3.dev3"

description:
  creates custom genome from reference genome and two phased VCF files SNPs and Indels

requirements:
  - $import: ../envvar-global.cwl

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
    source: "#tophat/tophatOut"

steps:

  - id: tophat
    run: test-tophat2.cwl
    inputs:
    - {id: r, default: 20}
    - {id: bowtie_index, default: {class: File, path: test_data/test_ref.1.bt2}}
    - {id: fastq1, default: {class: File, path: test_data/reads_1.fq}}
    - {id: fastq2, default: {class: File, path: test_data/reads_2.fq}}
    - {id: o, default: testwork}
    outputs:
    - {id: tophatOut}

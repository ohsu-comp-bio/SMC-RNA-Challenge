#!/usr/bin/env cwl-runner
#
# Author: thomas.yu@sagebase.org

class: Workflow

cwlVersion: "cwl:draft-3"

description:
  creates custom genome from reference genome and two phased VCF files SNPs and Indels

inputs: 
  - id: inputbedpe
    type: File

  - id: outputbedpe
    type: string

  - id: truthfile
    type: File

  - id: evaloutput
    type: string
  
  - id: geneAnnotationFile
    type: File

outputs:

  - id: output
    type: ["null",File]
    source: "#evaluator/evaluatoroutput"

  - id: error
    type: ["null",File]
    source: "#evaluator/errorlog"

steps:

  - id: validator
    run: ../validator.cwl
    inputs:
    - {id: inputbedpe, source: "#inputbedpe"}
    - {id: outputbedpe, source: "#outputbedpe"}
    outputs:
    - {id: validatoroutput}
    - {id: errorlog}

  - id: evaluator
    run: ../evaluator.cwl
    inputs:
    - {id: inputbedpe, source: "#validator/validatoroutput"}
    - {id: error, source: "#validator/errorlog"}
    - {id: truthfile, source: "#truthfile"}
    - {id: output, source: "#evaloutput"}
    - {id: geneAnnotationFile, source: "#geneAnnotationFile"}
    outputs:
    - {id: evaluatoroutput}
    - {id: errorlog}
#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3"

class: CommandLineTool

description: "Isoform quantification evaluator and validator"

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: dreamchallenge/smcrna-functions

inputs:

  - id: input
    type: File
    inputBinding:
      prefix: --input
      position: 1

  - id: geneAnnotationFile
    type: File
    inputBinding:
      prefix: --gtf
      position: 1

outputs:
  - id: evaluatoroutput
    type: File
    outputBinding:
      glob: result.out

baseCommand: [evaluation.py,evaluateIsoformQuant]


#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3"

class: CommandLineTool

description: |
  evaluation is developed for SMC-RNA Challenge
  Original tool usage: #update tool usage

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: dreamchallenge/smcrna-functions

# The position determines where the commands are placed in command line
inputs:

  - id: truthfile
    type: File
    description: | 
      bedpe-refer to SMC-RNA
    inputBinding:
      prefix: --truthfile
      position: 1
  
  - id: inputbedpe
    type: ["null",File]
    description: | 
      bedpe-refer to SMC-RNA
    inputBinding:
      prefix: --inputbedpe
      position: 1

  - id: error
    type: ["null",File]
    description: | 
      error.log to SMC-RNA
    inputBinding:
      prefix: --error
      position: 1

  - id: geneAnnotationFile
    type: File
    description: |
      Gene annotation file- refer to SMC-RNA
    inputBinding:
      prefix: --gtf
      position: 1

  - id: output
    type: string
    inputBinding:
      prefix: --outputbedpe
      position: 1

outputs:
  - id: evaluatoroutput
    type: ["null",File]
    outputBinding:
      glob: $(inputs.output)

  - id: errorlog
    type: ["null",File]
    outputBinding:
      glob: error.log

baseCommand: [evaluation.py,evaluate]


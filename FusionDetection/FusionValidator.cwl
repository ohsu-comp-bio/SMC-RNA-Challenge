#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3"

class: CommandLineTool

description: |
  Validation of Fusion Detection Challenge

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: dreamchallenge/smcrna-functions

inputs:
  
  - id: inputbedpe
    type: File
    description: | 
      bedpe-refer to SMC-RNA
    inputBinding:
      prefix: --inputbedpe
      position: 1

  - id: outputbedpe
    type: string
    inputBinding:
      prefix: --outputbedpe
      position: 1

outputs:
  - id: validatoroutput
    type: ["null",File]
    outputBinding:
      glob: $(inputs.outputbedpe)

  - id: errorlog
    type: ["null",File]
    outputBinding:
      glob: error.log

baseCommand: [evaluation.py,validate]


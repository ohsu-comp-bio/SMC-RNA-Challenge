#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [evaluation.py,evaluateFusionQuant]

doc: "Fusion Quantification validation and evaluation"

hints:
  DockerRequirement:
    dockerPull: dreamchallenge/smcrna-functions

requirements:
  - class: InlineJavascriptRequirement

inputs:

  - id: truth
    type: File
    inputBinding:
      prefix: --truth
      position: 1
  
  - id: input
    type: File
    inputBinding:
      prefix: --input
      position: 1

outputs:
  - id: output
    type: File
    outputBinding:
      glob: result.out



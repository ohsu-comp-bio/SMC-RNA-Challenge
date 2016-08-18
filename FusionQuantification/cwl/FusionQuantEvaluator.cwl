#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

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

  truth:
    type: File
    inputBinding:
      prefix: --truth
      position: 1
  
  input:
    type: File
    inputBinding:
      prefix: --input
      position: 1

outputs:

  output:
    type: File
    outputBinding:
      glob: result.out



#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [evaluation.py,evaluateFusionDet]

doc: "Fusion Detection validation and evaluation"

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

  gtf:
    type: File
    inputBinding:
      prefix: --gtf
      position: 1

  o:
    type:string
    inputputBinding:
      prefix: -o
      position: 2

outputs:

  output:
    type: File
    outputBinding:
      glob: $(inputs.o)



#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [evaluation.py,evaluateIsoformQuant]

doc: "Isoform quantification evaluator and validator"

hints:
  DockerRequirement:
    dockerPull: dreamchallenge/smcrna-functions

requirements:
  - class: InlineJavascriptRequirement

inputs:

  input:
    type: File
    inputBinding:
      prefix: --input
      position: 1
  
  truth:
    type: File
    inputBinding:
      prefix: --truth
      position: 1
  
  gtf:
    type: File
    inputBinding:
      prefix: --gtf
      position: 1

outputs:

  output:
    type: File
    outputBinding:
      glob: result.out



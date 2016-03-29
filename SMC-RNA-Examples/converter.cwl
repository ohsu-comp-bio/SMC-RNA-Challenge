#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3.dev3"

class: CommandLineTool

description: |
  converter.cwl is developed for SMC-RNA Challenge

  Original tool usage: #update tool usage

#Import other CWL files
requirements:
  - class: InlineJavascriptRequirement
  - $import: envvar-global.cwl
  - $import: converter-docker.cwl

# The position determines where the commands are placed in command line
inputs:

  - id: "#input"
    type: File
    inputBinding:
      position: 1

  - id: "#output"
    type: string

outputs:
  - id: "#fusionout"
    type: File
    outputBinding:
      # The output file is align_summary.txt
      # Make sure the output files match
      glob: $(inputs.output)

stdout: $(inputs.output)

baseCommand: ["convert_tophapt_to_bedpe.py"]

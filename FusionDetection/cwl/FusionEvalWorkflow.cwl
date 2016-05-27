#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

class: Workflow

cwlVersion: "draft-3"

description: "Fusion Detection Validator/Evaluator workflow"

inputs: 

  - id: truth
    type: File
  
  - id: input
    type: File

  - id: gtf
    type: File

outputs:

  - id: output
    type: ["null",File]
    source: "#evaluator/output"

steps:

  - id: evaluator
    run: FusionEvaluator.cwl
    inputs:
    - {id: truth, source: "#truth"}
    - {id: input, source: "#input"}
    - {id: gtf, source: "#gtf"}
    outputs:
    - {id: output}
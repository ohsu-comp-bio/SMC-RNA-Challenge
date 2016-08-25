#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

class: Workflow
cwlVersion: v1.0

doc: "Fusion Detection Validator/Evaluator workflow"

inputs: 

  truth:
    type: File
  
  input:
    type: File

  gtf:
    type: File

  o:
    type: string

outputs:

  - id: OUTPUT
    type: File?
    outputSource: evaluator/output

steps:

  evaluator:
    run: FusionEvaluator.cwl
    in:
      truth: truth
      input: input
      gtf: gtf
      o: o
    out: [output]
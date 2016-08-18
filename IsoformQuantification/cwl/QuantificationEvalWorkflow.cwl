#!/usr/bin/env cwl-runner
#
# Authors: Thomas Yu, Ryan Spangler, Kyle Ellrott

class: Workflow
cwlVersion: v1.0

doc: "Isoform Quantification Validator/Evaluator workflow"

inputs: 

  truth:
    type: File
  
  input:
    type: File

  gtf:
    type: File

outputs:

  OUTPUT:
    type: File?
    outputSource: evaluator/output

steps:

  evaluator:
    run: QuantificationEvaluator.cwl
    in:
      truth: truth
      input: input
      gtf: gtf
    out: [output]
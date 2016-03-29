#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3.dev3"

class: CommandLineTool

description: |
  tophat2.cwl is developed for SMC-RNA Challenge

  Original tool usage: #update tool usage

#Import other CWL files
requirements:
  - class: InlineJavascriptRequirement
  - $import: envvar-global.cwl
  - $import: tophat2-docker.cwl

# The position determines where the commands are placed in command line
inputs:

  ## Not required fields ##
  #Adding the ["null",type] allows you to designate a variable that is not required
  #Don't input a prefix field and it won't display a prefix

  - id: r
    type: ["null",int]
    inputBinding:
      position: 2
      prefix: -r

  - id: p
    type: ["null",int]
    description: | 
      Change number of threads used
    inputBinding:
      position: 2
      prefix: -p

  - id: mate-std-dev
    type: ["null",int]
    inputBinding:
      position: 2
      prefix: --mate-std-dev

  - id: max-intron-length
    type: ["null",int]
    inputBinding:
      position: 2
      prefix: --max-intron-length

  - id: fusion-min-dist
    type: ["null",int]
    inputBinding:
      position: 2
      prefix: --fusion-min-dist

  - id: fusion-anchor-length
    type: ["null",int]
    inputBinding:
      position: 2
      prefix: --fusion-anchor-length

  - id: fusion-ignore-chromosomes
    type: ["null",string]
    inputBinding:
      position: 2
      prefix: --fusion-ignore-chromosomes

  # Boolean values, shows prefix only
  - id: fusion-search
    type: ["null",boolean]
    description: | 
      Turn on fusion algorithm (tophat-fusion)
    inputBinding:
      prefix: --fusion-search
      position: 2

  - id: keep-fasta-order
    type: ["null",boolean]
    description: | 
      Keep ordering of fastq file
    inputBinding:
      prefix: --keep-fasta-order
      position: 2
  
  - id: bowtie1
    type: ["null",boolean]
    description: | 
      Use bowtie1
    inputBinding:
      prefix: --bowtie1
      position: 2

  - id: no-coverage-search
    type: ["null",boolean]
    description: | 
      Turn off coverage-search, which takes lots of memory and is slow
    inputBinding:
      prefix: --no-coverage-search
      position: 2

  ## Required files ##
  
  - id: fastq1
    type: File
    inputBinding:
      position: 4

  - id: fastq2
    type: File
    inputBinding:
      position: 5
  
  ## output of tophat is the directory ##
  - id: o
    type: string
    inputBinding:
      prefix: -o
      position: 1

  - id: bowtie_index
    type: File
      #type: array
      #items: File
    secondaryFiles:
      - ^^.2.ebwt
      - ^^.3.ebwt
      - ^^.4.ebwt
      - ^^.rev.1.ebwt
      - ^^.rev.2.ebwt
    default:
      class: File
      path: test_data/test_ref.1.ebwt

outputs:
  - id: tophatOut
    type: File
    outputBinding:
      # The output file is align_summary.txt
      # Make sure the output files match
      glob: $(inputs.o+'/fusions.out')

baseCommand: [tophat]
arguments:
  - valueFrom: $(inputs.bowtie_index.path.slice(0,-6))
    position: 3
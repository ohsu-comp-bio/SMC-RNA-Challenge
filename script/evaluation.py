#! /usr/bin/env python

import os
import sys
import argparse
import subprocess

def evaluateFusionDet(args):
	try:
		val = subprocess.check_call(["bedpeValidatorS.py", "-c", "/opt/SMC-RNA-Challenge/FusionDetection/Validator/GRCh37.chromosome.strict.txt", "-i",args.input])
	except Exception as e:
		val = str(e)
	if val == 0:
		evaluate = subprocess.check_call(["fusionToolEvaluator", "-t", args.truth,"-r",args.input,"-g", args.gtf,"-s","/opt/SMC-RNA-Challenge/FusionDetection/Evaluator/rulefile.txt","-o","result.out"])
	else:
		with open("result.out",'w') as results:
			results.write(val)
			results.close()

def evaluateIsoformQuant(args):
	try:
		val = subprocess.check_call(["quantificationValidator.py", "-g", args.gtf, "-i", args.input])
	except Exception as e:
		val = str(e)
	if val == 0:
		evaluate = subprocess.check_call(["quantificationEvaluator.py", "-t", args.truth, "-i", args.input])
	else:
		with open("result.out",'w') as results:
			results.write(val)
			results.close()

# ------------------------------------------------------------
# Args parse
# ------------------------------------------------------------
def perform_main(args):
	if 'func' in args:
		try:
			args.func(args)
		except Exception as ex:
			print(ex)

parser = argparse.ArgumentParser(description='Evaluate submission')

subparsers = parser.add_subparsers(title='commands',
		description='The following commands are available:')

parser_evaluateIsoformQuant = subparsers.add_parser('evaluateIsoformQuant',
		help='validates and evaluates isoform quantification challenge')
parser_evaluateIsoformQuant.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
parser_evaluateIsoformQuant.add_argument('--input',  metavar='results.out', type=str, required=True,
		help='transcriptId, TPM'),
parser_evaluateIsoformQuant.add_argument('--truth', help='Truth file', metavar='truth.isoforms.txt',type=str,required=True)
parser_evaluateIsoformQuant.set_defaults(func=evaluateIsoformQuant)

parser_evaluateFusionDet = subparsers.add_parser('evaluateFusionDet',
		help='validates and evaluates Fusion Detection challenge')
parser_evaluateFusionDet.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
parser_evaluateFusionDet.add_argument('--input',  metavar='results.bedpe', type=str, required=True,
		help='bedpe format file'),
parser_evaluateFusionDet.add_argument('--truth', help='Truth file', metavar='truth.bedpe',type=str,required=True)
parser_evaluateFusionDet.set_defaults(func=evaluateFusionDet)

#Parse args
args = parser.parse_args()
perform_main(args)
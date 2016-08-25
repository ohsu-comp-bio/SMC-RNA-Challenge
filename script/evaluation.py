#! /usr/bin/env python

import os
import sys
import argparse
import subprocess

def evaluateFusionDet(args):
	validator_path = os.path.join(os.path.dirname(__file__), "..", "FusionDetection", "Validator", "bedpeValidatorS.py")
	chrom_path = os.path.join(os.path.dirname(__file__), "..", "FusionDetection", "Validator", "GRCh37.chromosome.strict.txt")
	rule_file = os.path.join(os.path.dirname(__file__), "..", "FusionDetection", "Evaluator", "rulefile.txt")
	try:
		val = subprocess.Popen([validator_path, "-c", chrom_path, "-i",args.input],stdout=subprocess.PIPE)
		output = val.stdout.read()
	except Exception as e:
		output = str(e)
		print(output)
	if output == "Validated\n":
		evaluate = subprocess.check_call(["fusionToolEvaluator", "-t", args.truth,"-r",args.input,"-g", args.gtf,"-s",rule_file,"-o","detection_result.out"])
	else:
		with open("detection_result.out",'w') as results:
			results.write(output)
			results.close()

def evaluateFusionQuant(args):
	validator_path = os.path.join(os.path.dirname(__file__), "..", "FusionDetection", "Validator", "bedpeValidatorS.py")
	chrom_path = os.path.join(os.path.dirname(__file__), "..", "FusionDetection", "Validator", "GRCh37.chromosome.strict.txt")
	evaluator_path = os.path.join(os.path.dirname(__file__), "..", "FusionQuantification", "Evaluator", "fusionQuantificationEvaluator.py")
	print(validator_path)
	print(chrom_path)
	print(evaluator_path)
	try:
		val = subprocess.Popen([validator_path, "-c", chrom_path, "-i",args.input],stdout=subprocess.PIPE)
		output = val.stdout.read()
		print(output)
	except Exception as e:
		output = str(e)
		print(output)
	if output == "Validated\n":
		evaluate = subprocess.check_call([evaluator_path, "-t", args.truth,"-i",args.input])
	else:
		with open("quantification_result.out",'w') as results:
			results.write(output)
			results.close()

def evaluateIsoformQuant(args):
	validator_path = os.path.join(os.path.dirname(__file__), "..", "IsoformQuantification", "Validator", "quantificationValidator.py")
	evaluator_path = os.path.join(os.path.dirname(__file__), "..", "IsoformQuantification", "Evaluator", "quantificationEvaluator.py")
	try:
		val = subprocess.Popen([validator_path, "-g", args.gtf, "-i", args.input],stdout=subprocess.PIPE)
		output = val.stdout.read()
	except Exception as e:
		output = str(e)
		print(output)
	if output == "Validated\n":
		evaluate = subprocess.check_call([evaluator_path, "-t", args.truth, "-i", args.input])
	else:
		with open("result.out",'w') as results:
			results.write(output)
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
parser_evaluateIsoformQuant.add_argument('--gtf', help='Gene annotation file', metavar='Homo_sapiens.GRCh37.75.gtf',type=str,required=True)
parser_evaluateIsoformQuant.add_argument('--input',  metavar='results.out', type=str, required=True,
		help='transcriptId, TPM'),
parser_evaluateIsoformQuant.add_argument('--truth', help='Truth file', metavar='truth.isoforms.txt',type=str,required=True)
parser_evaluateIsoformQuant.set_defaults(func=evaluateIsoformQuant)

parser_evaluateFusionDet = subparsers.add_parser('evaluateFusionDet',
		help='validates and evaluates Fusion Detection challenge')
parser_evaluateFusionDet.add_argument('--gtf', help='Fusion Detection gene annotation file (syn5908245)', metavar='Homo_sapiens.GRCh37.75.txt',type=str,required=True)
parser_evaluateFusionDet.add_argument('--input',  metavar='results.bedpe', type=str, required=True,
		help='bedpe format file'),
parser_evaluateFusionDet.add_argument('--truth', help='Truth file', metavar='truth.bedpe',type=str,required=True)
parser_evaluateFusionDet.add_argument('-o', help='Output file', metavar='detection_result.out',type=str,required=True)
parser_evaluateFusionDet.set_defaults(func=evaluateFusionDet)

parser_evaluateFusionQuant = subparsers.add_parser('evaluateFusionQuant',
		help='validates and evaluates Fusion Quantification challenge')
parser_evaluateFusionQuant.add_argument('--input',  metavar='results.bedpe', type=str, required=True,
		help='bedpe format file'),
parser_evaluateFusionQuant.add_argument('--truth', help='Truth file', metavar='truth.bedpe',type=str,required=True)
parser_evaluateFusionQuant.set_defaults(func=evaluateFusionQuant)
#Parse args
args = parser.parse_args()
perform_main(args)
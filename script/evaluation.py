#! /usr/bin/env python

import os
import sys
import argparse
import subprocess

# def validate(args):
# 	val = subprocess.Popen(["bedpeValidatorS.py", "-s", "-c", "/opt/SMC-RNA-Challenge/FusionDetection/Validator/GRCh37.chromosome.strict.txt", "-i",args.inputbedpe , "-o", args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# 	out = val.stdout.read()
# 	error = val.stderr.read()
# 	if out != '' or error != '':
# 		with open("error.log",'w') as errors:
# 			errors.write("Error!\n")
# 			errors.write(out+"\n")
# 			errors.write(error)
# 			errors.close()

# def evaluate(args):
# 	if args.error is not None:
# 		os.system("cat %s > error.log" % args.error)
# 	else:
# 		evaluate = subprocess.Popen(["fusionToolEvaluator", "-t", args.truthfile,"-r",args.inputbedpe,"-g", args.gtf,"-s","/opt/SMC-RNA-Challenge/FusionDetection/Evaluator/rulefile.txt","-o",args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# 		out = evaluate.stdout.read()
# 		error = evaluate.stderr.read()

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
		val = "success"
		#evaluate = subprocess.check_call(["quantificationEvaluator", "-t", args.truth, "-i", args.input])
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

#Evaluate bedpe
# parser_evaluate = subparsers.add_parser('evaluate',
# 		help='evaluates input bedpe')
# parser_evaluate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, default=None,
# 		help='result bedpe'),
# parser_evaluate.add_argument('--error',  metavar='error.log', type=str, default=None,
# 		help='error log'),
# parser_evaluate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
# 		help='output bedpe')
# parser_evaluate.add_argument('--truthfile', metavar='truth.bedpe', type=str, required=True,
# 		help='truth file')
# parser_evaluate.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
# parser_evaluate.set_defaults(func=evaluate)

# #Validate bedpe
# parser_validate = subparsers.add_parser('validate',
# 		help='validates input bedpe')
# parser_validate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, required=True,
# 		help='result bedpe'),
# parser_validate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
# 		help='output bedpe')
# parser_validate.set_defaults(func=validate)

parser_evaluateIsoformQuant = subparsers.add_parser('evaluateIsoformQuant',
		help='validates and evaluates isoform quantification challenge')
parser_evaluateIsoformQuant.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
parser_evaluateIsoformQuant.add_argument('--input',  metavar='results.out', type=str, required=True,
		help='transcriptId, TPM'),
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
#! /usr/bin/env python

import os
import argparse
import subprocess

def validate(args):
	val = subprocess.Popen(["./bedpeValidatorS.py", "-s", "-c", "/opt/SMC-RNA-Challenge/FusionDetection/Validator/GRCh37.chromosome.strict.txt", "-i",args.inputbedpe , "-o", args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out = val.stdout.read()
	error = val.stderr.read()
	if out != '' or error != '':
		with open("error.log",'w') as errors:
			errors.write("Error!\n")
			errors.write(out+"\n")
			errors.write(error)
			errors.close()

def evaluate(args):
	if args.error is not None:
		os.system("cat %s > error.log" % args.error)
	else:
		evaluate = subprocess.Popen(["fusionToolEvaluator", "-t", args.truthfile,"-r",args.inputbedpe,"-g", args.gtf,"-s","/opt/SMC-RNA-Challenge/FusionDetection/Evaluator/rulefile.txt","-o",args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		out = evaluate.stdout.read()
		error = evaluate.stderr.read()

def evaluateIsoformQuant(args):
	try:
		val = subprocess.check_call(["./quantificationValidator.py", "-g", args.gtf, "-i", args.input])
	except Exception as e:
		val = e
		print(val)
		# with open("error.log",'w') as errors:
		# 	errors.write("Error!\n")
		# 	errors.write(out+"\n")
		# 	errors.write(error)
		# 	errors.close()
	if val == 0:
		print("Success")
		#evaluate = subprocess.check_call(["./quantificationEvaluator", "-t", args.truth, "-i", args.input])
		# with open("score.txt",'w') as errors:
		# 	errors.write("Error!\n")
		# 	errors.write(out+"\n")
		# 	errors.write(error)
		# 	errors.close()



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
parser_evaluate = subparsers.add_parser('evaluate',
		help='evaluates input bedpe')
parser_evaluate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, default=None,
		help='result bedpe'),
parser_evaluate.add_argument('--error',  metavar='error.log', type=str, default=None,
		help='error log'),
parser_evaluate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
		help='output bedpe')
parser_evaluate.add_argument('--truthfile', metavar='truth.bedpe', type=str, required=True,
		help='truth file')
parser_evaluate.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
parser_evaluate.set_defaults(func=evaluate)

#Validate bedpe
parser_validate = subparsers.add_parser('validate',
		help='validates input bedpe')
parser_validate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, required=True,
		help='result bedpe'),
parser_validate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
		help='output bedpe')
parser_validate.set_defaults(func=validate)

parser_evaluateIsoformQuant = subparsers.add_parser('evaluateIsoformQuant',
		help='validates and evaluates isoform quantification challenge')
parser_evaluate.add_argument('--gtf', help='Gene annotation file', metavar='ensemble.hg19.txt',type=str,required=True)
parser_validate.add_argument('--input',  metavar='results.out', type=str, required=True,
		help='transcriptId, TPM'),
parser_validate.set_defaults(func=evaluateIsoformQuant)

#Parse args
args = parser.parse_args()
perform_main(args)
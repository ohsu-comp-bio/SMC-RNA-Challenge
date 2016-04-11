#! /usr/bin/env python

import os
import argparse
import subprocess

def validate(args):
	val = subprocess.Popen(["python","/opt/SMC-RNA-Challenge/Validator/bedpeValidator.py", "-s", "-c", "/opt/SMC-RNA-Challenge/Validator/GRCh37.chromosome.strict.txt", "-i",args.inputbedpe , "-o", args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out = val.stdout.read()
	error = val.stderr.read()
	if out != '' or error != '':
		with open("error.log",'w') as errors:
			errors.write("Error!\n")
			errors.write(out+"\n")
			errors.write(error)
			errors.close()

def evaluate(args):
	if os.path.basename(args.inputbedpe) == "error.log":
		os.system("cat %s > error.log" % args.inputbedpe)
	else:
		evaluate = subprocess.Popen(["fusionToolEvaluator", "-t", args.truthfile,"-r",args.inputbedpe,"-g", args.gtf,"-s",args.rulefile,"-o",args.outputbedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		out = evaluate.stdout.read()
		error = evaluate.stderr.read()

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
parser_evaluate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, required=True,
		help='result bedpe'),
parser_evaluate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
		help='output bedpe')
parser_evaluate.add_argument('--truthfile', metavar='truth.bedpe', type=str, required=True,
		help='truth file')
parser_evaluate.add_argument('--rulefile', metavar='rulefile.txt', type=str, required=True,
		help='rule file')
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

#Parse args
args = parser.parse_args()
perform_main(args)
#! /usr/bin/env python

import os
import argparse

def evaluate(args):
	val = subprocess.Popen(["python","Validator/bedpeValidator.py", "-c", "Validator/GRCh37.chromosome.strict.txt", "-i",args.inputbedpe , "-o", args.outputBedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out = val.stdout.read()
	error = val.stderr.read()
	if out == '' and error == '':
		evaluate = subprocess.Popen(["fusionToolEvaluator", "-t", arg.truthfile,"-r",args.outputBedpe,"-g", "examples/ensembl.hg19.txt","-s","examples/rulefile.txt","-o",args.outputBedpe], stdout=subprocess.PIPE,stderr=subprocess.PIPE)


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

#Update beatAML project
parser_evaluate = subparsers.add_parser('eval',
		help='validates then evaluates input bedpe')
parser_evaluate.add_argument('--inputbedpe',  metavar='fusion.bedpe', type=str, required=True,
		help='result bedpe'),
parser_evaluate.add_argument('--outputbedpe', metavar='fusionout.bedpe', type=str, required=True,
		help='output bedpe')
parser_evaluate.add_argument('--truthfile', metavar='truth.bedpe', type=str, required=True,
		help='truth file')
parser_evaluate.set_defaults(func=evaluate)

#Parse args
args = parser.parse_args()
perform_main(args)
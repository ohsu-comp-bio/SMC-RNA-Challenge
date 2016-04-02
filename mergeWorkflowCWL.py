#! /usr/bin/env python

import yaml
import json
import os
import sys

fileName = sys.argv[1].split(".")
os.system("cwltool --print-deps %s > %s_dep.json" % (sys.argv[1],fileName[0]))
workflowjson = "%s_dep.json" % (fileName[0])

with open(workflowjson) as data_file:    
	data = json.load(data_file)
	if data.get('secondaryFiles',None) is None:
		raise ValueError("No secondary files to Merge")
	else:
		combined = []
		#Dependencies:
		for dep in data['secondaryFiles']:
			depcwl = open(dep['path'][7:],"r")
			docs = yaml.load(depcwl)
			docs['id'] = str(os.path.basename(dep['path']))
			del docs['cwlVersion']
			combined.append(docs)
		#Workflow
		workflow = open(data['path'][7:],"r")
		docs = yaml.load(workflow)
		del docs['cwlVersion']
		docs['id'] = str(os.path.basename(data['path']))
		for steps in docs['steps']:
			steps['run'] = "#" + steps['run']
			for i in steps['inputs']:
				if i.get('source',False):
					i['source'] = "#%s/%s" % (docs['id'],i['source'][1:])
		for steps in docs['outputs']:
			steps['source'] = "#%s/%s" % (docs['id'],steps['source'][1:])
		combined.append(docs)
		merged = {"cwlVersion":"cwl:draft-3","$graph":combined}

		with open('%s_merged.cwl' %fileName[0], 'w') as outfile:
			outfile.write(yaml.dump(merged))
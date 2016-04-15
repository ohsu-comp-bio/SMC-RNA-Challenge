#!/usr/bin/env python

import sys
import os
import argparse
import json
import gzip
import re
import traceback
import urlparse
import tarfile
import logging
import subprocess
import time
import yaml
from xml.dom.minidom import parse as parseXML

try:
    import requests
except ImportError:
    print "Please Install the requests library"
    print ">>> pip install requests"
    sys.exit(1)

try:
    import synapseclient
    from synapseclient import File, Folder, Project
    from synapseclient import Evaluation, Submission, SubmissionStatus
except ImportError:
    print "Please Install Synapse Client Library"
    print ">>> pip install synapseclient"
    sys.exit(1)

try:
    import vcf
except ImportError:
    vcf = None

#Some of the evaluation interface methods require an up-to-date copy of the Synapse client
try:
    from distutils.version import StrictVersion
    if StrictVersion(re.sub(r'\.dev\d+', '', synapseclient.__version__)) < StrictVersion('1.0.0'):
        print "Please Upgrade Synapse Client Library"
        print ">>> pip install -U synapseclient"
        sys.exit(1)
except ImportError:
    pass


CONFIG_FILE = os.path.join(os.environ['HOME'], ".dreamSubmitConfig")

CHALLENGE_ADMIN_TEAM_ID = 3322844
EVALUATION_QUEUE_ID = 5877348

def validate_workflow(syn,args):
    try:
        test = subprocess.check_call(["cwltool", "--non-strict", "--print-pre", args.CWLfile])
    except Exception as e:
        raise ValueError("Your CWL file is not formatted correctly",e)

    print "Checking Workflow"
    with open(args.CWLfile,"r") as cwlfile:
        try:
            docs = yaml.load(cwlfile)
        except Exception as e:
            raise Exception("Must be a CWL file (Yaml format)")

    assert docs['cwlVersion'] == 'cwl:draft-3'
    if docs.get('$graph',None) is None:
        raise ValueError("Please run 'python smc_rna_submit.py merge --CWLfile workflow.cwl'")
    else:
        cwltools = []
        workflowinputs = []
        workflowsteps = []
        workflowoutputs = []
        merged = docs['$graph']
        for tools in merged:
            if tools['class'] == 'CommandLineTool':
                for i in tools['inputs']:
                    cwltools.append("%s/%s/%s" % ("input",tools['id'],i['id']))
                for i in tools['outputs']:
                    cwltools.append("%s/%s/%s" % ("output",tools['id'],i['id']))
            else:
                assert tools['class'] == 'Workflow', 'CWL Classes can only be named "Workflow" or "CommandLineTool'
                for i in tools['inputs']:
                    workflowinputs.append("#%s/%s" % (tools['id'],i['id']))
                for i in tools['steps']:
                    for y in i['outputs']:
                        workflowoutputs.append("#%s/%s/%s" %(tools['id'],i['id'],y['id']))
                    workflowinputs = workflowinputs + workflowoutputs
                    for y in i['inputs']:
                        workflowsteps.append("%s/%s/%s" % ("input",i['run'][1:],y['id']))
                        if 'source' in y:
                            assert y['source'] in workflowinputs, 'Not all of your inputs in your workflow are mapped'
                for i in tools['outputs']:
                    if 'source' in i:
                        assert i['source'] in workflowoutputs, 'Your workflow output is not mapped correctly'
        for i in workflowsteps:
            assert i in cwltools, 'Your tool inputs do not match your workflow inputs'
        return 1


def give_synapse_permissions(syn, synapse_object, principal_id):
    acl = syn._getACL(synapse_object)
    acl['resourceAccess'].append({
        'principalId': principal_id,
        'accessType': [
            'CREATE',
            'READ',
            'SEND_MESSAGE',
            'DOWNLOAD',
            'UPDATE',
            'UPDATE_SUBMISSION',
            'READ_PRIVATE_SUBMISSION']})
    print "ACL", acl
    syn._storeACL(synapse_object, acl)
    return acl


def name_clean(name):
    return re.sub(r'[^\w]', "_", name)


def submit_workflow(syn, args):
    """
    Submit to challenge
    """
    try:
        validate_workflow(syn, args)
        if args.projectId is None:
            project = syn.store(Project("SMC-RNA-Challenge %s %s" % (syn.getUserProfile().userName, time.time())))
        CWL = syn.store(File(args.CWLfile, parent = project))
        print "Submitting workflow %s" % (CWL.name)
        submission = syn.submit(EVALUATION_QUEUE_ID, CWL, name=CWL.name, team=args.teamName)
        print "Created submission ID: %s" % submission.id
    except Exception as e:
        print(e)
    ## When you submit, you grant permissions to the Admin team
    #syn.setAnnotations(syn.get(output['workflow_entity']), submission)
    #give_synapse_permissions(syn, syn.get(project_id), CHALLENGE_ADMIN_TEAM_ID)


def merge(syn, args):
    CWLfile = args.CWLfile
    fileName = CWLfile.split(".")
    os.system("cwltool --print-deps %s > %s_dep.json" % (CWLfile,fileName[0]))
    workflowjson = "%s_dep.json" % (fileName[0])

    with open(workflowjson) as data_file:    
        data = json.load(data_file)
        if data.get('secondaryFiles',None) is None:
            raise ValueError("No secondary files to Merge")
        else:
            combined = []
            #Dependencies
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Submit Files to the DREAM mutation calling challenge. Please see https://www.synapse.org/#!Synapse:syn312572/wiki/60703 for usage instructions.')
    #Stack.addJobTreeOptions(parser)
    parser.add_argument("--synapse_email", help="Synapse UserName", default=None)
    parser.add_argument("--password", help="Synapse password", default=None)

    subparsers = parser.add_subparsers(title='commands',
            description='The following commands are available:')

    parser_merge = subparsers.add_parser('merge',
            help='Merge all CWL files into one CWL file')
    parser_merge.add_argument('--CWLfile',  metavar='workflow.cwl', type=str, required=True,
            help='CWL workflow file')
    parser_merge.set_defaults(func=merge)

    parser_validate = subparsers.add_parser('validate',
            help='Validate CWL file')
    parser_validate.add_argument('--CWLfile',  metavar='workflow_merged.cwl', type=str, required=True,
            help='CWL workflow file')
    parser_validate.set_defaults(func=validate_workflow)

    parser_submit = subparsers.add_parser('submit',
            help='Submit CWL file')
    parser_submit.add_argument('--CWLfile',  metavar='workflow_merged.cwl', type=str, required=True,
            help='CWL workflow file')
    parser_submit.add_argument('--teamName',  metavar='My Team', type=str, default = None,
            help='Challenge team name, leave blank if not part of a team')
    parser_submit.add_argument('--projectId',  metavar='syn123', type=str, default = None,
            help='Synapse Id of a project that you want the submission to be uploaded to, will create a project automatically if no projectId is specified')
    parser_submit.set_defaults(func=submit_workflow)

    # parser_validateAndSubmit = subparsers.add_parser('validateAndSubmit',
    #         help='Validate and Submit CWL file')
    # parser_validateAndSubmit.add_argument('--CWLfile',  metavar='workflow.cwl', type=str, required=True,
    #         help='CWL workflow file')
    # parser_validateAndSubmit.add_argument('--teamName',  metavar='My Team', type=str, default = None,
    #         help='Challenge team name, leave blank if not part of a team')
    # parser_validateAndSubmit.add_argument('--projectId',  metavar='syn123', type=str, default = None,
    #         help='Synapse Id of a project that you want the submission to be uploaded to, will create a project automatically if no projectId is specified')
    # parser_validateAndSubmit.set_defaults(func=validateAndSubmit)

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    if args.synapse_email is not None and args.synapse_key is not None:
        syn.login(email=args.synapse_email, password=args.password)
    else:
        if 'SYNAPSE_APIKEY' in os.environ and 'SYNAPSE_EMAIL' in os.environ:
            syn.login(email=os.environ['SYNAPSE_EMAIL'], apiKey=os.environ['SYNAPSE_APIKEY'])
        else:
            syn.login()


def perform_main(syn, args):
    if 'func' in args:
        try:
            args.func(syn,args)
        except Exception as ex:
            print(ex)

perform_main(syn, args)


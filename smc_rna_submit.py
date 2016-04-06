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

def validate_workflow(workflow):
    try:
        test = subprocess.check_call(["cwltool", "--print-pre", workflow])
    except Exception as e:
        raise ValueError("Your CWL file is not formatted correctly",e)

    print "Checking Workflow"
    with open(workflow,"r") as cwlfile:
        try:
            docs = yaml.load(cwlfile)
        except Exception as e:
            raise Exception("Must be a CWL file (Yaml format)")

    assert docs['cwlVersion'] == 'cwl:draft-3'
    if docs.get('$graph',None) is None:
        raise ValueError("Did not run mergeWorkflowCWL.py on main workflow.cwl")
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


def main_submit(syn, CWLfile, indexFilesFolder=None,project_id=None,teamName = None):
    """
    """
    ## When you submit, you grant permissions to the Admin team
    #syn.setAnnotations(syn.get(output['workflow_entity']), submission)
    #give_synapse_permissions(syn, syn.get(project_id), CHALLENGE_ADMIN_TEAM_ID)
    if project_id is None:
        project = syn.store(Project("SMC-RNA-Challenge %s %s" % (syn.getUserProfile().userName, time.time())))
    CWL = syn.store(File(CWLfile, parent = project))
    if indexFilesFolder is not None:
        print("wooo")
    print "Submitting workflow %s" % (CWL.name)
    submission = syn.submit(EVALUATION_QUEUE_ID, CWL, name=CWL.name, team=teamName)
    print "Created submission ID: %s" % submission.id


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Submit Files to the DREAM mutation calling challenge. Please see https://www.synapse.org/#!Synapse:syn312572/wiki/60703 for usage instructions.')
    #Stack.addJobTreeOptions(parser)
    parser.add_argument("--synapse_email", help="Synapse UserName", default=None)
    parser.add_argument("--password", help="Synapse password", default=None)

    parser.add_argument("--CWLfile", help="CWL file for submission", required=True)
    parser.add_argument("--meta", help="Submission Metadata", required=False)
    
    parser.add_argument("--teamname", help="Synapse team name",default=None)

    parser.add_argument("--project-id", help="The SYN id of your personal private working directory")

    parser.add_argument("--check", action="store_true",default=False)

    parser.add_argument("--submit", action="store_true", default=False)
    parser.add_argument("--no_upload",action="store_true",default=False)

    parser.add_argument("-w", "--indexFilesFolder",help="/path/to/index/file/folder/",default=None)

    args = parser.parse_args()
    if not args.no_upload:
        syn = synapseclient.Synapse()
        if args.synapse_email is not None and args.synapse_key is not None:
            syn.login(email=args.synapse_email, password=args.password)
        else:
            if 'SYNAPSE_APIKEY' in os.environ and 'SYNAPSE_EMAIL' in os.environ:
                syn.login(email=os.environ['SYNAPSE_EMAIL'], apiKey=os.environ['SYNAPSE_APIKEY'])
            else:
                syn.login()
    else:
        syn = None


    submit = args.submit
    run_check = args.check

    if run_check:
        validated = validate_workflow(args.CWLfile)
    if validated and submit:
        main_submit(syn, args.CWLfile)
    



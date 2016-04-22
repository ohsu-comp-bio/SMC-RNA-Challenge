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
import shutil
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
    print("\n\n###VALIDATING MERGED WORKFLOW###\n\n")
    try:
        test = subprocess.check_call(["cwltool", "--non-strict", "--print-pre", args.CWLfile])
    except Exception as e:
        raise ValueError("Your CWL file is not formatted correctly",e)

    with open(args.CWLfile,"r") as cwlfile:
        try:
            docs = yaml.load(cwlfile)
        except Exception as e:
            raise Exception("Must be a CWL file (Yaml format)")

    assert docs['cwlVersion'] == 'cwl:draft-3'
    if docs.get('$graph',None) is None:
        raise ValueError("Please run 'python smc_rna_submit.py merge --CWLfile %s'" % args.CWLfile)
    else:
        requiredInputs = []
        cwltools = []
        workflowinputs = []
        workflowoutputs = []
        merged = docs['$graph']
        synId = None
        for tools in merged:
            if tools['class'] == 'CommandLineTool':
                for i in tools['inputs']:
                    cwltools.append("%s/%s/%s" % ("input",tools['id'],i['id']))
                for i in tools['outputs']:
                    cwltools.append("%s/%s/%s" % ("output",tools['id'],i['id']))
            else:
                #Check: Workflow class
                assert tools['class'] == 'Workflow', 'CWL Classes can only be named "Workflow" or "CommandLineTool'
                for i in tools['inputs']:
                    workflowinputs.append("#%s/%s" % (tools['id'],i['id']))
                    if i.get('synData',None) is not None:
                        synId = i['synData']
                #Check: synData must exist as an input (tarball of the index files)
                if synId is None:
                    raise ValueError("""Must have synData as a parameter in an input (This is the synapse ID of the tarball of your index files): ie.
                                        -id: index
                                        -type: File
                                        -synData: syn12345
                                     """)
                else:
                    indexFiles = syn.get(synId,downloadFile=False)
                    acls = syn._getACL(indexFiles)
                    for acl in acls['resourceAccess']:
                        if acl['principalId'] == CHALLENGE_ADMIN_TEAM_ID:
                            assert 'READ' in acl['accessType'], "At least View/READ access has to be given to the SMC_RNA_Admins Team: (Team ID: 3322844)"
                #Check: Must contain these four inputs in workflow step
                for i in ["TUMOR_FASTQ_1","TUMOR_FASTQ_2"]:
                    required = "#%s/%s" % (tools['id'],i)
                    assert required in workflowinputs, "Your workflow MUST contain at least these four inputs: 'TUMOR_FASTQ_1','TUMOR_FASTQ_2'"
                for i in tools['steps']:
                    for y in i['outputs']:
                        workflowoutputs.append("#%s/%s/%s" %(tools['id'],i['id'],y['id']))
                    workflowinputs = workflowinputs + workflowoutputs
                    for y in i['inputs']:
                        #Check: Workflow tool steps match the cwltools inputs
                        steps = "%s/%s/%s" % ("input",i['run'][1:],y['id'])
                        assert steps in cwltools, 'Your tool inputs do not match your workflow inputs'
                        #Check: All sources used are included in the workflow inputs
                        if 'source' in y:
                            assert y['source'] in workflowinputs, 'Not all of your inputs in your workflow are mapped'
                for i in tools['outputs']:
                    assert i['id'] == 'FUSION_OUTPUT', "Your workflow output id must be FUSION_OUTPUT"
                    #Check: All outputs have the correct sources mapped
                    if 'source' in i:
                        assert i['source'] in workflowoutputs, 'Your workflow output is not mapped correctly to your tools'
    print("\n\nYour workflow passed validation!")
    return 1


def give_synapse_permissions(syn, synapse_object, principal_id):
    acl = syn._getACL(synapse_object)
    acl['resourceAccess'].append({
        'principalId': principal_id,
        'accessType': ['READ']})
    print "ACL", acl
    syn._storeACL(synapse_object, acl)
    return acl


def name_clean(name):
    return re.sub(r'[^\w]', "_", name)


def submit_workflow(syn, args):
    """
    Submit to challenge
    """

    print(args.CWLfile)

    args.CWLfile = merge(syn, args)
    try:
        validate_workflow(syn, args)
        print("\n\n###SUBMITTING MERGED WORKFLOW: %s###\n\n" % args.CWLfile)
        if args.projectId is None:
            print "No projectId is specified, a project is being created"
            project = syn.store(Project("SMC-RNA-Challenge %s %s" % (syn.getUserProfile().userName, time.time())))
            args.projectId = project['id']
            print "View your project here: https://www.synapse.org/#!Synapse:%s" % args.projectId
        CWL = syn.store(File(args.CWLfile, parent = project))
        submission = syn.submit(EVALUATION_QUEUE_ID, CWL, name=CWL.name, team=args.teamName)
        print "Created submission ID: %s" % submission.id
    except Exception as e:
        print(e)
    ## When you submit, you grant permissions to the Admin team
    give_synapse_permissions(syn, syn.get(args.projectId), CHALLENGE_ADMIN_TEAM_ID)
    print("Administrator access granted to challenge admins")



def merge(syn, args):
    print("\n\n###MERGING WORKFLOW###\n\n")

    CWLfile = os.path.basename(args.CWLfile)

    fileName = CWLfile.split(".")[0]
    outputDirectory = os.path.join("/".join(os.path.abspath(args.CWLfile).split("/")[:-1]),"submission_files")
    fileName = name_clean(fileName)
    print(fileName)
    try:
        os.mkdir(outputDirectory)
    except Exception as e:
        print(e)
    print(args.CWLfile)
    workflowjson = "%s_dep.json" % os.path.join(outputDirectory,fileName)
    os.system('cwltool --print-deps "%s" > %s' % (args.CWLfile,workflowjson))

    workflow = open(args.CWLfile)
    docs = yaml.load(workflow)
    #If CWL workflow isn't merged, then merge them
    if "$graph" not in docs:
        with open(workflowjson) as data_file:    
            data = json.load(data_file)
            if data.get('secondaryFiles',None) is None:
                raise ValueError("No secondary files to Merge")
            else:
                combined = []
                #Dependencies (CWLtools)
                for dep in data['secondaryFiles']:
                    depcwl = open(dep['path'][7:],"r")
                    docs = yaml.load(depcwl)
                    docs['id'] = str(os.path.basename(dep['path']))
                    del docs['cwlVersion']
                    combined.append(docs)
                #Workflow (steps)
                workflow = open(data['path'][7:],"r")
                docs = yaml.load(workflow)
                del docs['cwlVersion']
                docs['id'] = str(os.path.basename(data['path']))
                for steps in docs['steps']:
                    steps['run'] = "#" + os.path.basename(steps['run'])
                    for i in steps['inputs']:
                        if i.get('source',False):
                            i['source'] = "#%s/%s" % (docs['id'],i['source'][1:])
                for steps in docs['outputs']:
                    steps['source'] = "#%s/%s" % (docs['id'],steps['source'][1:])
                combined.append(docs)
                merged = {"cwlVersion":"cwl:draft-3","$graph":combined}

                with open('%s_%s_merged.cwl' %(os.path.join(outputDirectory,fileName),str(time.time()).split('.')[0]), 'w') as outfile:
                    outfile.write(yaml.dump(merged))
        args.CWLfile = '%s_%s_merged.cwl' % (os.path.join(outputDirectory,fileName),str(time.time()).split('.')[0])
    else:
        shutil.copy(args.CWLfile, os.path.join(outputDirectory,fileName))
        print("CWL files are already merged")
    os.remove(workflowjson)
    return(args.CWLfile)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Submit Files to the DREAM mutation calling challenge. Please see https://www.synapse.org/#!Synapse:syn312572/wiki/60703 for usage instructions.')
    #Stack.addJobTreeOptions(parser)
    parser.add_argument("--synapse_user", help="Synapse UserName", default=None)
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

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    if args.synapse_user is not None and args.password is not None:
        print("You only need to provide credentials once then it will remember your login information")
        syn.login(email=args.synapse_user, password=args.password,rememberMe=True)
    else:
        syn.login()


def perform_main(syn, args):
    if 'func' in args:
        try:
            args.func(syn,args)
        except Exception as ex:
            print(ex)

perform_main(syn, args)


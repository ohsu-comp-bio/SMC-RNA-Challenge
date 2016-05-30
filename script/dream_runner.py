#!/usr/bin/env python

import os
import yaml
import shutil
import argparse
import subprocess
import synapseclient
import json

def synapse_login(args):
    synapse = synapseclient.Synapse()
    if args.synapse_user is not None and args.synapse_password is not None:
        print('You only need to provide credentials once then it will remember your login information')
        synapse.login(email=args.synapse_user, password=args.synapse_password,rememberMe=True)
    else:
        synapse.login()

    return synapse

def validate_cwl(cwlpath):
    try:
        test = subprocess.check_call(['cwltool', '--print-pre', cwlpath])
    except Exception as e:
        raise ValueError('Your CWL file is not formatted correctly', e)

def load_cwl(cwlpath):
    with open(cwlpath, 'r') as cwlfile:
        try:
            cwl = yaml.load(cwlfile)
        except Exception as e:
            raise Exception('Must be a CWL file (YAML format)')

    return cwl

##Change this code
def find_synapse_data(cwl):
    input = filter(lambda input: input.get('synData', None) is not None, cwl['inputs'])[0]
    return input['synData']

def call_cwl(tool, inputs):
    arguments = ["cwl-runner",
                 "--cachedir", "./",
                 # "--tmpdir-prefix", "/data/tmp",
                 # "--tmp-outdir-prefix", "/data/tmp",
                 tool]
    arguments.extend(inputs)
    process = subprocess.Popen(arguments,stdout=subprocess.PIPE)
    output = process.stdout.read()
    temp = json.loads(output)
    return(temp['output']['path'])

def call_workflow(cwl, fastq1, fastq2, index_path):
    inputs = ["--index", index_path,
              "--TUMOR_FASTQ_1", fastq1,
              "--TUMOR_FASTQ_2", fastq2]

    output = call_cwl(cwl, inputs)
    return(output)

def call_evaluation(cwl, workflow_output, truth, annotations):
    # local = "eval-workflow.cwl"
    # shutil.copyfile(cwl, local)
    inputs = ["--input", workflow_output,
              "--truth", truth,
              "--gtf", annotations]

    call_cwl(cwl, inputs)
    # os.remove(local)

def run_dream(synapse, args):
    cwlpath = args.workflow_cwl
    validate_cwl(cwlpath)
    cwl = load_cwl(cwlpath)
    synapse_id = find_synapse_data(cwl)

    print("SYNAPSE: " + synapse_id)

    # index = synapse.get(synapse_id, downloadLocation="/data")
    index = synapse.get(synapse_id)
    workflow_out = call_workflow(args.workflow_cwl, args.fastq1, args.fastq2, index.path)
    call_evaluation(args.eval_cwl, workflow_out, args.truth, args.annotations)

def download(synapse,args):
    try:
        subprocess.check_call(["gsutil", "ls" ,"gs://dream-smc-rna"])
    except Exception as e:
        raise ValueError("You are not logged in to gcloud.  Please login by doing 'gcloud auth login' and follow the steps to have access to the google bucket")
    arguments = None
    dry_run = ["30m","100m","100m_gt","all"]
    training = ['sim1','sim2','sim3','sim4','sim5','sim7','sim8','sim11','sim13','sim14','sim15','sim16','sim17','sim19','sim21']
    if args.training is not None:
        if args.training in training:
            data = "gs://dream-scm-rna/training/%s_*" % args.training
            arguments = ["gsutil","cp",data, args.dir]
        else:
            raise ValueError("Must pass in one of these options for downloading training data: %s" % ', '.join(training))
    if args.dryrun is not None:
        path = "gs://dream-scm-rna/for_dry_run"
        bedpe_truth = os.path.join(path,"sim1a_30m_truth.bedpe")
        if args.training == "30m"
            isoform_truth = os.path.join(path,"sim_diploid_30m.sim.isoforms.results_truth")
            data =  os.path.join(path,"sim1a_30m_merged_*")
        elif args.training == "100m":
            isoform_truth = os.path.join(path,"sim_diploid_100m.sim.isoforms.results_truth")
            data =  os.path.join(path,"sim1a_100m_merged_*") 
        elif args.training == "100m_gt":
            isoform_truth = os.path.join(path,"sim_diploid_100m_gt1.sim.isoforms.results_truth")
            data =  os.path.join(path,"sim1a_100m_gt1_merged_*")
        elif args.training == "all":
            isoform_truth = os.path.join(path,"*isoforms*")
            data = os.path.join(path,"*merged*")
        else:
            raise ValueError("Must pass in one of these options for downloading training data: %s" % ', '.join(dry_run))
        arguments = ["gsutil","cp",bedpe_truth,isoform_truth,data,args.dir]
    if arguments is not None:
        subprocess.check_call(arguments)
    else:
        print("You did not pick any training or dry run data to download")


def perform_main(args):
    synapse = synapse_login(args)
    if 'func' in args:
        try:
            args.func(synapse,args)
        except Exception as ex:
            print(ex)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DREAM runner - run your workflow from beginning to end.')
    parser.add_argument('--synapse-user', help='synapse Username', default=None)
    parser.add_argument('--synapse-password', help='synapse password', default=None)
    
    subparsers = parser.add_subparsers(title='commands',description='The following commands are available:')
    
    parser_run = subparsers.add_parser('run',help='Runs workflow and evaluation framework')
    parser_run.add_argument('--workflow-cwl',  default='smc-tophat-workflow.cwl', type=str, help='cwl workflow file')
    parser_run.add_argument('--eval-cwl',  default='eval-workflow.cwl', type=str, help='cwl workflow file')
    parser_run.add_argument('--fastq1', default='sim1a_30m_merged_1.fq.gz')
    parser_run.add_argument('--fastq2', default='sim1a_30m_merged_2.fq.gz')
    parser_run.add_argument('--truth', default='truth.bedpe')
    parser_run.add_argument('--annotations', default='ensembl.hg19.txt')
    parser_run.set_defaults(func=run_dream)
    
    parser_download = subparsers.add_parser('download',help='Downloads training and dry-run data')
    parser_download.add_argument('--training', default=None, type=str, 
        help='download training data: sim1, sim2, sim3, sim4, sim5, sim7, sim8, sim11, sim13, sim14, sim15, sim16, sim17, sim19, sim21')
    parser_download.add_argument('--dryrun', default=None, type=str, 
        help='download dry run data: 30m, 100m, 100m_gt')
    parser_download.add_argument('--dir', default="./", type=str, 
        help='Directory to download files to')
    parser_run.set_defaults(func=download)

    args = parser.parse_args()
    perform_main(args)
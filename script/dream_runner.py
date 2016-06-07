#!/usr/bin/env python

import os
import yaml
import shutil
import argparse
import subprocess
import traceback
import tempfile
import synapseclient
import json

DREAM_RNA_BUCKET = "gs://dream-smc-rna"
DREAM_TRAINING = ['sim1','sim2','sim3','sim4','sim5','sim7','sim8','sim11','sim13','sim14','sim15','sim16','sim17','sim19','sim21']
DREAM_DEBUG = ["dryrun1","dryrun2","dryrun3","dryrun4","dryrun5"]

REFERENCE_DATA = {
    "REFERENCE_GENOME" : "Homo_sapiens.GRCh37.75.dna_sm.primary_assembly.fa",
    "REFERENCE_GTF" : "Homo_sapiens.GRCh37.75.gtf"
}

FILE_SUFFIX = ["_filtered.bedpe", "_isoforms_truth.txt", "_mergeSort_1.fq.gz", "_mergeSort_2.fq.gz"]

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


def find_synapse_data(cwl):
    input = filter(lambda input: input.get('class', None) == "Workflow", cwl['$graph'])[0]
    return input['hints'][0]['entity']

def call_cwl(tool, inputs, nocache=False, cachedir = "cwl-cache"):
    if nocache:
        arguments = ["cwl-runner",tool]
    else:
        arguments = ["cwl-runner",
                     "--cachedir", cachedir,
                     tool]
    arguments.extend(inputs)
    try:
        print "Running: %s" % (" ".join(arguments))
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE)
        output, error = process.communicate()
        temp = json.loads(output)
        print temp
        return(temp['OUTPUT']['path'])
    except Exception, e:
        traceback.print_exc()
        print("Unable to call cwltool")
    #return(temp['output']['path'])

def call_workflow(cwl, fastq1, fastq2, index_path, nocache=False, cachedir="cwl-cache"):
    inputs = ["--index", index_path,
              "--TUMOR_FASTQ_1", fastq1,
              "--TUMOR_FASTQ_2", fastq2]

    output = call_cwl(cwl, inputs, nocache, cachedir)
    return(output)

def call_evaluation(cwl, workflow_output, truth, annotations, nocache=False, cachedir="cwl-cache"):
    # local = "eval-workflow.cwl"
    # shutil.copyfile(cwl, local)
    inputs = ["--input", workflow_output,
              "--truth", truth,
              "--gtf", annotations]

    call_cwl(cwl, inputs, nocache, cachedir)
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
        subprocess.check_call(["gsutil", "ls" ,DREAM_RNA_BUCKET])
    except Exception as e:
        raise ValueError("You are not logged in to gcloud.  Please login by doing 'gcloud auth login' and follow the steps to have access to the google bucket")
    if args.input in DREAM_TRAINING or args.input in DREAM_DEBUG:
        print("Caching Inputs files")
        for suf in FILE_SUFFIX:
            local_path = os.path.join(args.dir, args.input + suf)
            if not os.path.exists(local_path):
                if args.input in DREAM_TRAINING:
                    data = "%s/training/%s_*" % (DREAM_RNA_BUCKET, args.input)
                elif args.input in DREAM_DEBUG:
                    data = "%s/debugging/%s_*" % (DREAM_RNA_BUCKET, args.input)                    
                cmd = ["gsutil","cp", data, args.dir]
                subprocess.check_call(cmd)
    else:
        raise ValueError("Must pass in one of these options for downloading training/debugging data: %s" % ', '.join(DREAM_TRAINING + DREAM_DEBUG))

def run_test(syn,args):
    try:
        subprocess.check_call(["gsutil", "ls" ,DREAM_RNA_BUCKET])
    except Exception as e:
        raise ValueError("You are not logged in to gcloud.  Please login by doing 'gcloud auth login' and follow the steps to have access to the google bucket")
    if not os.path.exists(args.dir):
        print("Making directory %s" % args.dir)
        os.mkdir(args.dir)

    for ref in REFERENCE_DATA.values():
        if not os.path.exists(os.path.join(args.dir, ref)):
            cmd = ["gsutil", "cp", "%s/%s.gz" % (DREAM_RNA_BUCKET, ref), args.dir]
            subprocess.check_call(cmd)
            cmd = ["gunzip", os.path.join(args.dir, "%s.gz" % (ref))]
            subprocess.check_call(cmd)
        
    with open(args.workflow) as handle:
        doc = yaml.load(handle.read())
    custom_inputs = {}
    for hint in doc.get("hints", []):
        if 'synData' == hint.get("class", ""):
            ent = syn.get(hint['entity'])
            custom_inputs[hint['input']] = {
                "class" : "File",
                "path" : ent.path
            }
    download(syn, args)
    in_req = {
        "TUMOR_FASTQ_1" : {
            "class" : "File",
            "path" : os.path.abspath(os.path.join(args.dir, args.input + "_mergeSort_1.fq.gz"))
        },
        "TUMOR_FASTQ_2" : {
            "class" : "File",
            "path" : os.path.abspath(os.path.join(args.dir, args.input + "_mergeSort_2.fq.gz"))
        }
    }
    for k, v in REFERENCE_DATA.items():
        in_req[k] = {
            "class" : "File",
            "path" : os.path.abspath(os.path.join(args.dir, v))
        }
    for k, v in custom_inputs.items():
        in_req[k] = v
    print json.dumps(in_req, indent=4)
        
    tmp = tempfile.NamedTemporaryFile(dir=args.dir, prefix="dream_runner_input_", suffix=".json", delete=False)
    tmp.write(json.dumps(in_req))
    tmp.close()
    workflow_out = call_cwl(args.workflow, [tmp.name], args.no_cache, cachedir=args.cachedir)
    if args.challenge == "fusion":
        cwl = os.path.join(os.path.dirname(__file__),"..","FusionDetection","cwl","FusionEvalWorkflow.cwl")
        truth = os.path.abspath(os.path.join(args.dir, args.input + "_filtered.bedpe"))
        annots = syn.get("syn5908245")
        annotations = annots.path
    elif args.challenge == "isoform":
        cwl = os.path.join(os.path.dirname(__file__),"..","IsoformQuantification","cwl","QuantificationEvalWorkflow.cwl")
        truth = os.path.abspath(os.path.join(args.dir, args.input + "_isoforms_truth.txt"))
        annotations = os.path.abspath(os.path.join(args.dir, "Homo_sapiens.GRCh37.75.gtf"))
    else:
        raise ValueError("Please pick either 'fusion' or 'isoform' for challenges")
    call_evaluation(cwl, workflow_out, truth, annotations, args.no_cache, cachedir=args.cachedir)
            
def perform_main(args):
    synapse = synapse_login(args)
    if 'func' in args:
        try:
            args.func(synapse,args)
        except Exception as ex:
            print traceback.print_exc()
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
    parser_download.add_argument('input', type=str,
        help='download training or dry data: %s' % ( ", ".join(DREAM_TRAINING+DREAM_DEBUG)))
    parser_download.add_argument('--dir', default="./", type=str, 
        help='Directory to download files to')
    parser_download.set_defaults(func=download)
    
    parser_test = subparsers.add_parser('test',help='Downloads training and dry-run data')
    parser_test.add_argument("--dir", type=str, default="./",
        help='Directory to download data to')
    parser_test.add_argument("input", type = str,
        help='Training/debugging dataset to use: %s' % ( ", ".join(DREAM_TRAINING+DREAM_DEBUG)))
    parser_test.add_argument("workflow", type = str,
        help='Non merged workflow file')
    parser_test.add_argument("challenge", type = str,
        help='Choose the challenge question: fusion or isoform')
    parser_test.add_argument("--no-cache", action='store_true',
        help='Do not cache workflow steps')
    parser_test.add_argument("--cachedir", type=str, default="cwl-cache",
        help='Directory to cache cwl run')
    parser_test.set_defaults(func=run_test)
    args = parser.parse_args()
    perform_main(args)

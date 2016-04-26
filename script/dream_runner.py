import os
import yaml
import shutil
import argparse
import subprocess
import synapseclient

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
        test = subprocess.check_call(['cwltool', '--non-strict', '--print-pre', cwlpath])
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
    input = filter(lambda input: input.get('synData', None) is not None, cwl['inputs'])[0]
    return input['synData']

def call_cwl(tool, inputs):
    arguments = ["cwl-runner", "--non-strict", tool].extend(inputs)
    subprocess.check_call(arguments)    

def call_workflow(cwl, fastq1, fastq2, index_path):
    inputs = ["--index", index_path,
              "--TUMOR_FASTQ_1", fastq1,
              "--TUMOR_FASTQ_2", fastq2]

    call_cwl(cwl, inputs)

def call_evaluation(cwl, truth, annotation):
    local = "eval-workflow.cwl"
    shutil.copyfile(cwl, local)
    inputs = ["--inputbedpe", "filtered_fusion.bedpe",
              "--outputbedpe", "valid.bedpe",
              "--truthfile", truth,
              "--evaloutput", "result.out",
              "--geneAnnotationFile", annotation]

    call_cwl(local, inputs)
    os.remove(local)

def run_dream(synapse, args):
    cwlpath = args.workflow_cwl
    validate_cwl(cwlpath)
    cwl = load_cwl(cwlpath)
    synapse_id = find_synapse_data(cwl)

    print("SYNAPSE: " + synapse_id)

    index = synapse.get(synapse_id)
    call_workflow(args.workflow_cwl, args.fastq1, args.fastq2, index.path)
    call_evaluation(args.eval_cwl, args.truth, args.annotation)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DREAM runner - run your workflow from beginning to end.')
    parser.add_argument('--synapse-user', help='synapse Username', default=None)
    parser.add_argument('--synapse-password', help='synapse password', default=None)
    parser.add_argument('--workflow-cwl',  default='workflow/smc-tophat-workflow.cwl', type=str, help='cwl workflow file')
    parser.add_argument('--eval-cwl',  default='../SMC-RNA-Challenge/cwl/eval-workflow.cwl', type=str, help='cwl workflow file')

    parser.add_argument('--fastq1', default='sim1a_30m_merged_1.fq.gz')
    parser.add_argument('--fastq2', default='sim1a_30m_merged_2.fq.gz')
    parser.add_argument('--truth', default='input/truth.bedpe')
    parser.add_argument('--annotations', default='input/ensembl.hg19.txt')
                        
    args = parser.parse_args()
    synapse = synapse_login(args)

    run_dream(synapse, args)
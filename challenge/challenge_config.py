##-----------------------------------------------------------------------------
##
## challenge specific code and configuration
##
##-----------------------------------------------------------------------------

import synapseclient
import subprocess
import yaml
import os
import requests

## A Synapse project will hold the assetts for your challenge. Put its
## synapse ID here, for example
## CHALLENGE_SYN_ID = "syn1234567"
CHALLENGE_SYN_ID = "syn2813589"
CHALLENGE_ADMIN_TEAM_ID = 3322844
## Name of your challenge, defaults to the name of the challenge's project
CHALLENGE_NAME = "SMC-RNA Challenge"

## Synapse user IDs of the challenge admins who will be notified by email
## about errors in the scoring script
ADMIN_USER_IDS = ["3324230"]
PROVIDED = ["TUMOR_FASTQ_1","TUMOR_FASTQ_2","REFERENCE_GENOME","REFERENCE_GTF"]

## Each question in your challenge should have an evaluation queue through
## which participants can submit their predictions or models. The queues
## should specify the challenge project as their content source. Queues
## can be created like so:
##   evaluation = syn.store(Evaluation(
##     name="My Challenge Q1",
##     description="Predict all the things!",
##     contentSource="syn1234567"))
## ...and found like this:
##   evaluations = list(syn.getEvaluationByContentSource('syn3375314'))
## Configuring them here as a list will save a round-trip to the server
## every time the script starts.
evaluation_queues = [
{'contentSource': u'syn2813589',
 u'createdOn': u'2016-04-05T22:51:54.787Z',
 'description': u'Queue for workflow submission for the SMC-RNA Challenge',
 u'etag': u'b038273b-5c6f-436d-bfc2-8d76dd325e18',
 u'id': u'5877348',
 'name': u'SMC-RNA-Challenge-evaluation-queue',
 u'ownerId': u'3324230',
 'status': u'OPEN',
 'submissionInstructionsMessage': u'Please submit a merged CWL File',
 'submissionReceiptMessage': u'Thanks for submitting to SMC-RNA Challenge'},
 {u'contentSource': u'syn2813589',
 u'createdOn': u'2016-04-20T02:03:28.436Z',
 u'description': u'Detect and quantify isoforms present in simulated data, in Illumina short-read datasets containing spiked-in transcripts, and in long-read datasets.',
 u'etag': u'7fc1394e-876f-49e8-87e2-a6a398c01965',
 u'id': u'5952651',
 u'name': u'SMC-RNA-Challenge evaluation queue- Challenge 1-Isoforms',
 u'ownerId': u'3324230',
 u'quota': {u'submissionLimit': 3},
 u'status': u'OPEN',
 u'submissionInstructionsMessage': u'Submit a CWL file',
 u'submissionReceiptMessage': u'Thanks for submitting to SMC-RNA-Challenge- Challenge 1-Isoforms'}] 

evaluation_queue_by_id = {q['id']:q for q in evaluation_queues}

## define the default set of columns that will make up the leaderboard
LEADERBOARD_COLUMNS = [
    dict(name='objectId',      display_name='ID',      columnType='STRING', maximumSize=20),
    dict(name='userId',        display_name='User',    columnType='STRING', maximumSize=20, renderer='userid'),
    dict(name='entityId',      display_name='Entity',  columnType='STRING', maximumSize=20, renderer='synapseid'),
    dict(name='versionNumber', display_name='Version', columnType='INTEGER'),
    dict(name='name',          display_name='Name',    columnType='STRING', maximumSize=240),
    dict(name='team',          display_name='Team',    columnType='STRING', maximumSize=240)]

## Here we're adding columns for the output of our scoring functions, score,
## rmse and auc to the basic leaderboard information. In general, different
## questions would typically have different scoring metrics.
leaderboard_columns = {}
for q in evaluation_queues:
    leaderboard_columns[q['id']] = LEADERBOARD_COLUMNS + [
        dict(name='score',         display_name='Score',   columnType='DOUBLE'),
        dict(name='rmse',          display_name='RMSE',    columnType='DOUBLE'),
        dict(name='auc',           display_name='AUC',     columnType='DOUBLE')]

## map each evaluation queues to the synapse ID of a table object
## where the table holds a leaderboard for that question
leaderboard_tables = {}

## Testing link validation: 7155824
def validate(evaluation,submission,syn,token):
    assert isinstance(submission.entity, synapseclient.File), "Must submit a file entity"
    if submission.entity.externalURL is None:
        try:
            #test = subprocess.check_call(["cwltool", "--print-pre", submission.filePath])
            test = os.system("cwltool --print-pre %s" % submission.filePath)
        except Exception as e:
            raise ValueError("Your CWL file is not formatted correctly",e)

        with open(submission.filePath,"r") as cwlfile:
            try:
                docs = yaml.load(cwlfile)
            except Exception as e:
                raise Exception("Must be a CWL file (Yaml format)")
        version = docs['cwlVersion']
        assert version in  ['v1.0','draft-3'], "cwlVersion must be draft-3 or v1.0"
        if docs.get('$graph',None) is None:
            raise ValueError("Please run 'python smc_rna_submit.py merge --CWLfile %s'" % submission.filePath)
        else:
            requiredInputs = []
            cwltools = []
            workflowinputs = []
            workflowoutputs = []
            merged = docs['$graph']
            custom_inputs = dict()
            for tools in merged:
                if tools['class'] == 'CommandLineTool':
                    for i in tools['inputs']:
                        cwltools.append("%s/%s" % ("input",i['id']))
                    for i in tools['outputs']:
                        cwltools.append("%s/%s" % ("output",i['id']))
                else:
                    #Check: Workflow class
                    assert tools['class'] == 'Workflow', 'CWL Classes can only be named "Workflow" or "CommandLineTool'
                    workflow = tools
            #Check: Make sure hints for index files are formatted correctly
            hints = workflow.get("hints",None)
            if hints is not None:
                for i in hints:
                    if os.path.basename(i['class']) == "synData":
                        assert i.get('input', None) is not None or \
                               i.get('entity', None) is not None, """synData hint must be in this format:
                                                                                hints:
                                                                                  - class: synData
                                                                                    input: index
                                                                                    entity: syn12345
                                                                  """
                        custom_inputs[i['input']] = i['entity']

            for i in workflow['inputs']:
                workflowinputs.append("%s" % i['id'])
                if os.path.basename(i['id']) not in PROVIDED:
                    assert custom_inputs.get(os.path.basename(i['id']),None) is not None, "Custom inputs do not match hints"
                    #Check: if synData is used, they must have the correct ACL's
                    indexFiles = syn.get(custom_inputs.get(os.path.basename(i['id']),None),downloadFile=False)
                    acls = syn._getACL(indexFiles)
                    for acl in acls['resourceAccess']:
                        if acl['principalId'] == CHALLENGE_ADMIN_TEAM_ID:
                            assert 'READ' in acl['accessType'], "At least View/READ access has to be given to the SMC_RNA_Admins Team: (Team ID: 3322844)"

            #Check: Must contain at least tumor fastq1, 2 as inputs in workflow step
            for i in ["TUMOR_FASTQ_1","TUMOR_FASTQ_2"]:
                required = "#main/%s" % i
                assert required in workflowinputs, "Your workflow MUST contain at least these two inputs: 'TUMOR_FASTQ_1','TUMOR_FASTQ_2'"
            #Check: If all workflow inputs map to the custom or provided ids
            if len(workflowinputs) > (len(custom_inputs) + 2):
                for i in workflowinputs:
                    assert os.path.basename(i) in PROVIDED or os.path.basename(i) in custom_inputs, "Your specified input ids must be one of: %s" %  ", ".join(custom_inputs.keys()+PROVIDED)
            for i in workflow['steps']:
                #Check for v1.0 and draft-3
                if version == "draft-3":
                    inputs = "inputs"
                    outSource = "source"
                    for y in i['outputs']:
                        workflowoutputs.append(y['id'])
                else:
                    inputs = "in"
                    outSource = "outputSource"
                    for y in i['out']:
                        workflowoutputs.append(y)
                workflowinputs = workflowinputs + workflowoutputs
            #Must seperate the input and output colleciton steps
            for i in workflow['steps']:
                for y in i[inputs]:
                    #Check: Workflow tool steps match the cwltools inputs
                    if isinstance(i['run'],str):
                        steps = "%s/#%s/%s" % ("input",i['run'][1:],os.path.basename(y['id']))
                        assert steps in cwltools, 'Your tool inputs do not match your workflow inputs'
                    #Check: All sources used are included in the workflow inputs
                    if 'source' in y:
                        y['source'] = [y['source']] if isinstance(y['source'],str) else y['source']
                        assert all([source in workflowinputs for source in y['source']]), 'Not all of your inputs in your workflow are mapped'
            for i in workflow['outputs']:
                assert i['id'] == '#main/OUTPUT', "Your workflow output id must be OUTPUT"
                #Check: All outputs have the correct sources mapped
                if outSource in i:
                    assert i[outSource] in workflowoutputs, 'Your workflow output is not mapped correctly to your tools'
    else:
        assert submission.entity.externalURL.startswith('https://cgc.sbgenomics.com/u'), "Your input URL is not formatted correctly"
        BASE_URL = "https://cgc-api.sbgenomics.com/v2/"
        if submission.entity.externalURL.endswith("/"):
            submission.entity.externalURL = submission.entity.externalURL[:-1]
        task = requests.get(BASE_URL + "tasks/" + os.path.basename(submission.entity.externalURL), headers={"X-SBG-Auth-Token" : token} ).json()
        assert task.get('message') != "Unauthorized", "You must share your cgc workflow with 'smc-rna-admin'"
        assert task['status'] == 'COMPLETED', "The URL that you put in is invalid"

    return (True,"Passed validation!")


def score(evaluation,submission):
    return(dict(),"Thank you for your submission to the SMC-RNA Challenge!")


config_evaluations = [

    {
        'id':5952651,
        'score_as_part_of_challenge': False,
        'validation_function': validate,
        'scoring_function': score,

    },
    {
        'id':5877348,
        'score_as_part_of_challenge': False,
        'validation_function': validate,
        'scoring_function': score,

    }
]
config_evaluations_map = {ev['id']:ev for ev in config_evaluations}



def validate_submission(evaluation, submission, token):
    """
    Find the right validation function and validate the submission.

    :returns: (True, message) if validated, (False, message) if
              validation fails or throws exception
    """
    config = config_evaluations_map[int(evaluation.id)]
    validation_func = config['validation_function']
    syn = synapseclient.login()
    results = validation_func(evaluation,submission,syn, token)
    return results


def score_submission(evaluation, submission):
    """
    Find the right scoring function and score the submission

    :returns: (score, message) where score is a dict of stats and message
              is text for display to user
    """
    config = config_evaluations_map[int(evaluation.id)]
    scoring_func = config['scoring_function']

    results = scoring_func(evaluation,submission.filePath)
    return results



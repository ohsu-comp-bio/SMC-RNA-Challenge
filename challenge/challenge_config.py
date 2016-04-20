##-----------------------------------------------------------------------------
##
## challenge specific code and configuration
##
##-----------------------------------------------------------------------------

import synapseclient
import subprocess
import yaml
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
 'submissionReceiptMessage': u'Thanks for submitting to SMC-RNA Challenge'}] 

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


def validate_1(evaluation,submission):
    return (True,"Passed validation!")

def validate_2(evaluation,submission,syn):
    try:
        test = subprocess.check_call(["cwltool", "--non-strict", "--print-pre", submission])
    except Exception as e:
        raise ValueError("Your CWL file is not formatted correctly",e)

    print "Checking Workflow"
    with open(submission,"r") as cwlfile:
        try:
            docs = yaml.load(cwlfile)
        except Exception as e:
            raise Exception("Must be a CWL file (Yaml format)")

    assert docs['cwlVersion'] == 'cwl:draft-3'
    if docs.get('$graph',None) is None:
        raise ValueError("Please run 'python smc_rna_submit.py merge --CWLfile %s'" % submission)
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
                for i in ["TUMOR_FASTQ_1","TUMOR_FASTQ_2","TRUTH","GENE_ANNOTATIONS"]:
                    required = "#%s/%s" % (tools['id'],i)
                    assert required in workflowinputs, "Your workflow MUST contain at least these four inputs: 'TUMOR_FASTQ_1','TUMOR_FASTQ_2','TRUTH','GENE_ANNOTATIONS'"
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
                    #Check: All outputs have the correct sources mapped
                    if 'source' in i:
                        assert i['source'] in workflowoutputs, 'Your workflow output is not mapped correctly'
    return (True,"Passed validation!")


def score(evaluation,submission):
    return(dict(),"Thank you for your submission to the SMC-RNA Challenge!")


config_evaluations = [

    {
        'id':5952651,
        'score_as_part_of_challenge': False,
        'validation_function': validate_1,
        'scoring_function': score,

    },
    {
        'id':5877348,
        'score_as_part_of_challenge': False,
        'validation_function': validate_2,
        'scoring_function': score,

    }
]
config_evaluations_map = {ev['id']:ev for ev in config_evaluations}



def validate_submission(evaluation, submission):
    """
    Find the right validation function and validate the submission.

    :returns: (True, message) if validated, (False, message) if
              validation fails or throws exception
    """
    config = config_evaluations_map[int(evaluation.id)]
    validation_func = config['validation_function']
    syn = synapseclient.login()
    results = validation_func(evaluation,submission.filePath,syn)
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



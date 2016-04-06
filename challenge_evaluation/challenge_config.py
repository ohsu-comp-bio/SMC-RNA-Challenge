##-----------------------------------------------------------------------------
##
## challenge specific code and configuration
##
##-----------------------------------------------------------------------------


## A Synapse project will hold the assetts for your challenge. Put its
## synapse ID here, for example
## CHALLENGE_SYN_ID = "syn1234567"
CHALLENGE_SYN_ID = "syn2813589"

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


def validate(evaluation,submission):
    return (True,"Passed validation!")


def score(evaluation,submission):
    return(dict(),"Thank you for your submission to the SMC-RNA Challenge!")


config_evaluations = [

    {
        'id':5877348,
        'score_as_part_of_challenge': False,
        'validation_function': validate,
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

    results = validation_func(evaluation,submission)
    return results


def score_submission(evaluation, submission):
    """
    Find the right scoring function and score the submission

    :returns: (score, message) where score is a dict of stats and message
              is text for display to user
    """
    config = config_evaluations_map[int(evaluation.id)]
    scoring_func = config['scoring_function']

    results = scoring_func(evaluation,submission)
    return results



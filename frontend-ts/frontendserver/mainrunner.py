import supportingfunctions
import os
import json       
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session

ISTHISDEMO = os.getenv('ISTHISDEMO')
if ISTHISDEMO != 'True':selectionfile="selectionmap.json"
else:selectionfile="selectionmapdemo.json"

ENABLELABELCHECK = os.getenv('ENABLELABELCHECK')


with open(selectionfile, "r") as f:
    selectionmap=json.load(f)


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'secret'  # for session signing
app.config['SESSION_TYPE'] = 'filesystem'  # store sessions in temp dir
Session(app)

# Main entry point
# Define your endpoints
@app.route('/api/', methods=['GET', 'POST'])
def handle_request():
    global naicsindexselection
    """HTTP Cloud Function."""
    request_json = request.get_json(silent=True)
    request_args = request.args


    return jsonify(supportingfunctions.get_topicdefinitions(request_json))
    # Implement your request handling logic
    return request_args 
    
  
@app.route('/api/updateanalyticstables', methods=['POST'])
def UpdateAnalyticsPage():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400
    print('UpdateAnalyticsPage')
    print(company)   
    
    data = supportingfunctions.Runpopulatecurrentprogress(company)
    if not data:
        return jsonify({"error": "database for project not found"}), 400
        
    return jsonify({"status": "ok", "data": data}), 200
    
@app.route('/api/jobcompleted', methods=['POST'])
def ListeningForJobCompletion():
    request_json = request.get_json(silent=True)
    db_name = request_json['db_name']
    ## convert db name back to company/project name
    for company, records in selectionmap.items():
        if records['db_name']==db_name:break
    
    print('recieved job completion report, starting control switch')    
    supportingfunctions.runControlSwitch_async(company)

    return jsonify({"status": "Message Recieved, job completion report"}), 200
    
@app.route('/api/dbselection', methods=['POST'])
def DataBaseSelection():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if company =='':
        menueContent = supportingfunctions.initializeDBNames()
        return jsonify({"status": "db cached", "company": company, "menueContent":menueContent}), 200
        
    else:
        selected_db = supportingfunctions.selectDB(projectselected=company)  # store it
        return jsonify({"status": "db cached", "company": company}), 200
#    session['selected_company'] = company  # store in session
    return jsonify({"error": "no company selected"}), 400

@app.route('/api/getcurrentprogress', methods=['POST'])
def GetCurrentProgress():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400
    print('GetCurrentProgress')
    print(company)
    
    if 'progresstype' in request_json:
        match request_json['progresstype']:
            case 'overall':
                print(request_json['progresstype'])
                data = supportingfunctions.getdocumentsLabeledProgress(company)
            case 'reviewedstats':
                data = supportingfunctions.getReviewedStats(company)
            case 'listofpropogateddocuments':
                data = supportingfunctions.getTableofDocumentsProgress(company)
    
    else:
        data = supportingfunctions.getcurrentprogress(projectselected=company)
    if not data:
        return jsonify({"error": "database for project not found"}), 400
        
    return jsonify({"status": "ok", "data": data}), 200

@app.route('/api/getitemsinbucket', methods=['POST'])
def GetItemsinBucket():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    userinjesttype = request_json['userinjesttype'] 
    data=None
    if not company:
        return jsonify({"error": "no company selected"}), 400

    try:
        data = supportingfunctions.getitemsinstorage(projectselected=company)
        if userinjesttype!='' and data is not None:
            supportingfunctions.runControlSwitch_async(company, userinjesttype)
    except:return jsonify({"error": "database for project not found"}), 400
        
    return jsonify({"status": "ok", "data": data}), 200
    

@app.route('/api/addcategory', methods=['POST'])
def AddCategory():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400

    print(request_json)
    currentlistofdefinitions = supportingfunctions.addnewdefinitiontotable(request_json)
    return jsonify({"status": "ok", "data": currentlistofdefinitions}), 200    

@app.route('/api/getnextcandidatelabel', methods=['POST'])
def GetNextCandidateLabel():
    request_json = request.get_json(silent=True)
    print(request_json)
    
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400

    if request_json['markstagecomplete']=='complete':
        print('Yes Yes')
        supportingfunctions.func_defineLabelingasComplete(request_json)
        supportingfunctions.runControlSwitch_async(company)
        return jsonify({"status": "ok", "data": ""}), 200
    
    textforcandidates = supportingfunctions.getNextLabelCandidate(request_json)
    return jsonify({"status": "ok", "data": textforcandidates}), 200

@app.route('/api/getnextnearduplicate', methods=['POST'])
def GetNextNearDuplicate():
    request_json = request.get_json(silent=True)
    print(request_json)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400
        
    textfornearduplicatecandidates = supportingfunctions.get_candidate_sample(lo=request_json["lo"], hi=request_json["hi"], last_answer=request_json["last_answer"], projectselected=company, tolerance=0.005, percent_quantile=0.99)

    return jsonify({"status": "ok", "data": textfornearduplicatecandidates}), 200

@app.route('/api/action', methods=['POST'])
def respondtoindexquery():

    request_json = request.get_json(silent=True)
    print(request_json)
    if not request_json or any([i in request_json for i in ['random_sample' , 'least_confidence', 'search_text']]):
        return jsonify({"error": "Select atleast one category to sample"}), 400

    print('Returning Response of index search')

    ### if label reassignment is in this message, then do a label reassign
    rejectionStats=None
    if 'reassignlabels' in request_json:
        if request_json['reassignlabels']:
            rejectionStats = supportingfunctions.reassignlabelUser(request_json)
        else:
            rejectionStats = supportingfunctions.GetRejectionStats(request_json)
     
    print('rejectionStats')
    print(rejectionStats)
    rowsperpage=1
    offsetvalue = max([0,request_json['page']-1])*rowsperpage
    print('offsetvalue', offsetvalue)
    relevantRows = supportingfunctions.getrelevantdocuments(request_json, rowsperpage=rowsperpage, offsetvalue=offsetvalue)
    
    return jsonify({'data':relevantRows, 'rejectionStats':rejectionStats})

@app.route('/api/labelthiscandidate', methods=['POST'])
def GetUserLabel():

    request_json = request.get_json(silent=True)

    
    assignment = supportingfunctions.assignNewUserLabel(request_json)
    print('assignment')
    print(request_json)
    possibleMisMatch=[]
    if ENABLELABELCHECK=='True':
        possibleMisMatch = supportingfunctions.getPossibleMisLabels(request_json)
    print('possibleMisMatch')
    
    if assignment:
        return jsonify({"status": "ok", "data": request_json, 'mismatch':possibleMisMatch}), 200
    else:
        return jsonify({"error": "Could Not Assign Label"}), 400
    

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
    
    
    
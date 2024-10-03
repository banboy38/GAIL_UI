import flask


from utils import tender_json,bidders_json
import uuid
import os
from queue import Queue, Empty
from threading import Thread

from bidder_pipeline import bid_eval_doc_processor,bid_eval_doc_extractor
from time import sleep
import pandas as pd


app = flask.Flask(__name__)
app.secret_key="gailpockey"
DB_DETAILS={
    "tender":"database/tender_data.json",
    "bidders":"database/bidder_data.json"
}

DATA_UPLOAD_FOLDER = os.path.join("static", "uploads")


commands = Queue()

def game_loop():
    while True:
        try:
            command = commands.get_nowait()
            for files in command['pdf_file']:
                bidder=bidders_json.read_json(DB_DETAILS['bidders'])['bidders'][command['bidder_id']]
                bidder['status'][files]="Processing"
                bidders_json.update_json(command['bidder_id'], bidder, DB_DETAILS['bidders'])
                out=bid_eval_doc_processor({
                    "cba_path": command['cba_path'],
                    "pdf_file": files,
                    "bidder_name": command['bidder_name'],
                    "bidder_id": command['bidder_id'],
                    "bidder_path": command['bidder_path']
                })
                bidder['status'][files]="Completed"
                bidders_json.update_json(command['bidder_id'], bidder, DB_DETAILS['bidders'])
            bid_eval_doc_extractor(command)
        except Empty:
            pass
        sleep(5)  # TODO poll other things

Thread(target=game_loop, daemon=True).start()



@app.route('/',methods=['GET','POST'])
def index():
    if flask.request.args.get('status') ==None:
        all_tenders=tender_json.read_json(DB_DETAILS['tender'])
        tenders=all_tenders['tenders'].values()
        if flask.request.method=="POST":
            tender_id=flask.request.form.get("tender_id")
            tender_status=flask.request.form.get("tender_status")
           
        return flask.render_template('landingpage.html',
                                    tenders=tenders)
    else:
        all_tenders=tender_json.read_json(DB_DETAILS['tender'])
        tenders=all_tenders['tenders'].values()
        return flask.render_template('landingpage.html',
                                    tenders=tenders,
                                    status=flask.request.args.get('status'),
                                    message=flask.request.args.get('messages'))
    
    
@app.route('/create_new_tender/',methods=['GET','POST'])
def tender():
    if flask.request.args.get('tender_id') ==None:
        uid=str(uuid.uuid4())
        return flask.render_template('tenderpage.html',tender_id=uid)
    return flask.render_template('tenderpage.html')

@app.route('/bidders/<tender_id>',methods=['GET','POST'])
def bidders(tender_id):
   
    if flask.request.method=="POST":
        print("in here")
        bidder_name = flask.request.form.get('bidder_name')
        bidder_files = flask.request.files.getlist('bidder_files')
        print(bidder_files)
        bidder_id = str(uuid.uuid4())
        bidder_folder = os.path.join(DATA_UPLOAD_FOLDER, tender_id, 'bidders', bidder_id)

        if not os.path.exists(bidder_folder):
            os.makedirs(bidder_folder)

        saved_files = []
        for file in bidder_files:
            file_path = os.path.join(bidder_folder, file.filename)
            file.save(file_path)
            saved_files.append(file.filename)

        bidder_data = {
            "bidder_id": bidder_id,
            "bidder_name": bidder_name,
            "tender_id": tender_id,
            "documents": saved_files,
            "status":{
               f: 'Queued' for f in saved_files
            }
        }
        print(bidder_data)
        bidders_json.update_json(bidder_id, bidder_data, DB_DETAILS['bidders'])
        
        commands.put_nowait({"cba_path":  os.path.join(DATA_UPLOAD_FOLDER,tender_id,'cba',"CBA.xlsx"),
                            "pdf_file": saved_files,
                            "bidder_name": bidder_name,
                            "bidder_id": bidder_id,
                            "bidder_path": os.path.join(DATA_UPLOAD_FOLDER,tender_id,'bidders',bidder_id),
                            "out_path": os.path.join(DATA_UPLOAD_FOLDER,tender_id,'outputs')
                            })
    
    
    all_bidders=bidders_json.read_json(DB_DETAILS['bidders'])['bidders']
    filter_bidders=[v for b,v in all_bidders.items() if v['tender_id']==tender_id]
    
    return flask.render_template('bidders.html',bidders=filter_bidders,tender_id=tender_id)

@app.route('/bid_view/<bider_id>/',methods=['GET','POST'])
def bid_view(bider_id):
    bidder=bidders_json.read_json(DB_DETAILS['bidders'])['bidders'][bider_id]
    path=os.path.join(DATA_UPLOAD_FOLDER,bidder['tender_id'],'bidders',bider_id,"meta_info.csv")
    columns=[]
    data=[]
    if os.path.exists(path):
        df=pd.read_csv(path)
        columns=list(df.columns)
        data=df.values.tolist()
    
    return flask.render_template('bid_view.html',
                                 bidder_id=bider_id,
                                 bidder=bidder,
                                columns=columns,
                                data=data
                                 )
@app.route('/dashboard_tab/<tender_id>/',methods=['GET','POST'])
def dashboard_tab(tender_id):
    tender=tender_json.read_json(DB_DETAILS['tender'])['tenders'][tender_id]
    bidder=bidders_json.read_json(DB_DETAILS['bidders'])['bidders']
    columns=[]
    data=[]
    filters=[]
    bidder_list=[v for b,v in bidder.items() if v['tender_id']==tender_id]
    if os.path.exists(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'outputs',"extracted.csv")):
        df=pd.read_csv(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'outputs',"extracted.csv"))
        turn_over=df[df.Field.str.contains("annual turnover",case=False)].to_dict(orient='records')[0]
        turn_over={k:v for k,v in turn_over.items() if k not in ['Field',"Type of Parameter"]}
        net_worth=df[df.Field.str.contains("net worth",case=False)].to_dict(orient='records')[0]
        net_worth={k:v for k,v in net_worth.items() if k not in ['Field',"Type of Parameter"]}
        working_capital =df[df.Field.str.contains("working capital",case=False)].to_dict(orient='records')[0]
        working_capital={k:v for k,v in working_capital.items() if k not in ['Field',"Type of Parameter"]}
        columns=df.columns
        data=df.values.tolist()
        filters=df['Type of Parameter'].unique().tolist()
        filters=["_".join(filter.split()) for filter in filters]
    else:
        return flask.redirect(flask.url_for('index',status="Error",messages="Processing is still going on. Please check back later"))
    return flask.render_template('tab_summary.html',
                                 bidder_list=bidder_list,
                                 tender_id=tender_id,
                                 tender=tender,
                                 net_worth={
                                     "labels":list(net_worth.keys()),
                                     "values":list(net_worth.values())
                                     },
                                 working_capital={
                                     "labels":list(working_capital.keys()),
                                     "values":list(working_capital.values())
                                     },
                                 turn_over={
                                     "labels":list(turn_over.keys()),
                                     "values":list(turn_over.values())
                                     },
                                columns=df.columns,
                                data=df.values.tolist(),
                                filters=filters
                                 )
    


    

@app.route('/upload_tender_documents/', methods=['POST'])
def upload_tender_documents():
    print(flask.request.form)
    tender_id = flask.request.form.get("tender_id")
    tender_name = flask.request.form.get("tender_name")
    tender_number = flask.request.form.get("tender_number")
    issue_date = flask.request.form.get("issue_date")
    submission_date = flask.request.form.get("submission_date")
    
    tender_files = flask.request.files.getlist("tender_files[]")
    cba_file = flask.request.files.get("cba_file")
    if not os.path.exists(os.path.join(DATA_UPLOAD_FOLDER,tender_id)):
        os.makedirs(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'tenders'))
        os.makedirs(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'bidders'))
        os.makedirs(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'outputs'))
        os.makedirs(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'cba'))
        
    # Save the files to the server or process them as needed
    for tender_file in tender_files:
        tender_file.save(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'tenders',tender_file.filename))
    
    if cba_file:
        
        cba_file.save(os.path.join(DATA_UPLOAD_FOLDER,tender_id,'cba',"CBA.xlsx"))
    
    tender_data = {
        "tender_id":tender_id,
        "tender_name": tender_name,
        "tender_number": tender_number,
        "issue_date": issue_date,
        "submission_date": submission_date,
        "tender_files": [file.filename for file in tender_files],
        "cba_file": cba_file.filename if cba_file else None
    }
    
    tender_json.update_json(tender_id, tender_data, DB_DETAILS['tender'])
    
    return {"uid": tender_id}



@app.route('/upload_bidder_docs/', methods=['POST'])
def upload_bidder_docs():
    bidder_name = flask.request.form.get('bidder_name')
    bidder_files = flask.request.files.getlist('bidder_files')

    if not bidder_name or not bidder_files:
        return flask.jsonify({'error': 'Bidder name and files are required.'}), 400

    tender_id = flask.request.args.get('tender_id')
    if not tender_id:
        return flask.jsonify({'error': 'Tender ID is required.'}), 400

    bidder_id = str(uuid.uuid4())
    bidder_folder = os.path.join(DATA_UPLOAD_FOLDER, tender_id, 'bidders', bidder_id)

    if not os.path.exists(bidder_folder):
        os.makedirs(bidder_folder)

    saved_files = []
    for file in bidder_files:
        file_path = os.path.join(bidder_folder, file.filename)
        file.save(file_path)
        saved_files.append(file.filename)

    bidder_data = {
        "bidder_id": bidder_id,
        "bidder_name": bidder_name,
        "tender_id": tender_id,
        "documents": saved_files
    }

    bidders_json.update_json(bidder_id, bidder_data, DB_DETAILS['bidders'])

    return flask.jsonify({'message': 'Documents uploaded successfully!', 'bidder_id': bidder_id})



@app.route('/trigger/<name>')
def trigger(name):
    commands.put_nowait({"command": "triggered","name":name})
    return "triggered"


if __name__=='__main__':
    app.run(debug=False,port=5005)
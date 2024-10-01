import flask


from utils import tender_json,bidders_json

app = flask.Flask(__name__)
app.secret_key="gailpockey"
DB_DETAILS={
    "tender":"database/tender_data.json",
    "bidders":"database/bidder_data.json"
}

@app.route('/',methods=['GET','POST'])
def index():
    all_tenders=tender_json.read_json(DB_DETAILS['tender'])
    tenders=all_tenders['tenders'].values()
    if flask.request.method=="POST":
        tender_id=flask.request.form.get("tender_id")
        tender_status=flask.request.form.get("tender_status")
        print(tender_id,tender_status)
        return flask.render_template('landingpage.html',
                                 tenders=tenders)
    return flask.render_template('landingpage.html',
                                 tenders=tenders)
    
    

@app.route('/bidders/<tender_id>',methods=['GET','POST'])
def bidders(tender_id):
    all_bidders=bidders_json.read_json(DB_DETAILS['bidders'])['bidders']
    filter_bidders=[v for b,v in all_bidders.items() if v['tender_id']==tender_id]
    return flask.render_template('bidders.html',bidders=filter_bidders)


if __name__=='__main__':
    app.run(debug=True,port=5005)
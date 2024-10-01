import flask


from utils import tender_json

app = flask.Flask(__name__)
app.secret_key="gailpockey"
DB_DETAILS={
    "tender":"database/tender_data.json",
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


if __name__=='__main__':
    app.run(debug=True,port=5005)
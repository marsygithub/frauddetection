from flask import Flask, request, render_template
import json
import requests
import socket
import time
from datetime import datetime
import cPickle as pickle
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from flask.ext.pymongo import PyMongo



app = Flask(__name__)
mongo = PyMongo(app)
PORT = 5353
REGISTER_URL = "removed"
DATA = []
TIMESTAMP = []
payout_type = []
num_payouts = []
delivery_method = []
fraud_transactions = []





@app.route('/score', methods=['POST'])
def score():
    DATA.append(json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ': ')))
    TIMESTAMP.append(time.time())


    payout_type1 = (json.loads(DATA[-1])['payout_type'])
    if payout_type1 == '':
        payout_type1 = '0'
    elif payout_type1 == 'ACH':
        payout_type1 = '1'
    elif payout_type1 == 'CHECK':
        payout_type1 = '2'
    else:
        payout_type1 = '3'
    num_payouts1 = (json.loads(DATA[-1])['num_payouts'])
    delivery_method1 = (json.loads(DATA[-1])['delivery_method'])


    payout_type.append(payout_type1)
    num_payouts.append(num_payouts1)
    delivery_method.append(delivery_method1)

    df = pd.DataFrame({'num_payouts': num_payouts,
                        'payout_type': payout_type,
                        'delivery_method': delivery_method})
    df = df[['num_payouts', 'payout_type', 'delivery_method']]

    predictions = model.predict(df)

    print predictions[-1]
    if predictions[-1] == 1:
        store_data=json.loads(DATA[-1])
        table.insert(store_data)
        fraud_transactions.append(store_data)


    return ""

@app.route('/fraud')
def fraud():
    line1= "Number of Fraud Transactions: {0}".format(table.count())
    curr_name = table.find({"name":{'$exists': 1}},{"name" : 1, "org_name" : 1,"num_payouts" : 1, "country" : 1, '_id' : 0})
    name = []
    num_payouts = []
    country = []
    org_name = []
    for row in curr_name:
        if row == '':
            name.append(row['NA'])
            num_payouts.append(row['NA'])
            country.append(row['NA'])
            org_name.append(row['NA'])

        else:
            name.append(row['name'])
            num_payouts.append(row['num_payouts'])
            country.append(row['country'])
            org_name.append(row['org_name'])

    html_df = pd.DataFrame({'name': name, 'num_payouts': num_payouts, 'org_name': org_name, 'country': country})
    html_df = html_df[['name', 'org_name', 'country', 'num_payouts']]

    html_table = html_df.to_html()



    return render_template('index.html', table=html_table)

    #return '{0}\n\n{1}'.format(line1, line2), 200, {'Content-Type': 'text/css; charset=utf-8'}
    #return render_template('index.html', title = 'Flask - Bootstrap')

@app.route('/check')
def check():
    line1 = "Number of data points: {0}".format(len(DATA))
    if DATA and TIMESTAMP:
        dt = datetime.fromtimestamp(TIMESTAMP[-1])
        data_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        line2 = "Latest datapoint received at: {0}".format(data_time)
        line3 = DATA[-1]
        output = "{0}\n\n{1}\n\n{2}".format(line1, line2, line3)
    else:
        output = line1
    return output, 200, {'Content-Type': 'text/css; charset=utf-8'}


def register_for_ping(ip, port):
    registration_data = {'ip': ip, 'port': port}
    requests.post(REGISTER_URL, data=registration_data)


if __name__ == '__main__':
    db_cilent = MongoClient()
    db = db_cilent['fraud']
    table = db['transactions']
    with open("model.pkl") as f_un:
        model = pickle.load(f_un)


    # Register for pinging service
    ip_address = socket.gethostbyname(socket.gethostname())
    print "attempting to register %s:%d" % (ip_address, PORT)
    register_for_ping(ip_address, str(PORT))

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)

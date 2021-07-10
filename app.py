from flask import Flask, render_template, request, jsonify
from fetch_option_chain import * 
from main import *
from api_details import *

app = Flask(__name__, static_folder='static/',
static_url_path='',
template_folder='templates/')

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('frontend.html')

@app.route('/intra-day', methods=['GET'])
def intra_day():
    
    data = fetch_json('NIFTY', "nse")
    dates = get_expiry_dates(data)
    spotprice = get_underlying_asset_value(data)
    data = date_filter(data, dates[0])

    support_peaks = get_peaks(data, 'Put_OI', True, 'Put_change_in_OI')
    resistance_peaks = get_peaks(data, 'Call_OI', True, 'Call_change_in_OI')
    supp_keys = get_req_keys(support_peaks, spotprice, True)
    res_keys = get_req_keys(resistance_peaks, spotprice, False)

    return {
        'supp-levels' : supp_keys,
        'res-levels' : res_keys
    }
    

if __name__ == "__main__":
    app.run(debug=True)

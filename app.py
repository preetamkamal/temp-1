from flask import Flask, render_template
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

    support_key_levels  = get_keys(support_peaks, spotprice)
    resistance_key_levels = get_keys(resistance_peaks, spotprice)

    l1 = get_supp_num(support_key_levels)
    supp_score, sup_state = l1[0], l1[1]
    l2 = get_resis_num(resistance_key_levels)
    res_score, res_state = l2[0],l2[1]

    for i in range(len(support_key_levels)):
        if sup_state[i] == 1:
            support_key_levels[i].append('Bullish')
        elif sup_state[i] == -1:
            support_key_levels[i].append('Bearish')
        elif sup_state[i] == -0.5:
            support_key_levels[i].append('Weakly Bearish')
        else:
            support_key_levels[i].append('Weakly Bullish')
    
    for i in range(len(resistance_key_levels)):
        if res_state[i] == 1:
            resistance_key_levels[i].append('Bullish')
        elif res_state[i] == -1:
            resistance_key_levels[i].append('Bearish')
        elif res_state[i] == -0.5:
            resistance_key_levels[i].append('Weakly Bearish')
        else:
            resistance_key_levels[i].append('Weakly Bullish')


    column_names = ['Call_OI', 'Call_change_in_OI','Call_total_traded_vol', 'Call_net_change', 'StrikePrice', 'Put_net_change', 'Put_total_traded_vol', 'Put_change_in_OI', 'Put_OI', 'Trend']
    support_peaks = pd.DataFrame(support_key_levels, columns = column_names )
    resistance_peaks = pd.DataFrame(resistance_key_levels, columns = column_names)   

    supp_keys = get_req_keys(support_peaks, spotprice, True)
    res_keys = get_req_keys(resistance_peaks, spotprice, False)

    return {
        'supp-levels' : supp_keys,
        'res-levels' : res_keys 
    }


@app.route('/weekly', methods=['GET'])
def weekly():
    
    data = fetch_json('NIFTY', "nse")
    dates = get_expiry_dates(data)
    spotprice = get_underlying_asset_value(data)
    data = date_filter(data, dates[0])

    support_peaks = get_peaks(data, 'Put_OI', False, 'Put_change_in_OI')
    resistance_peaks = get_peaks(data, 'Call_OI', False, 'Call_change_in_OI')

    support_key_levels  = get_keys(support_peaks, spotprice)
    resistance_key_levels = get_keys(resistance_peaks, spotprice)

    l1 = get_supp_num(support_key_levels)
    supp_score, sup_state = l1[0], l1[1]
    l2 = get_resis_num(resistance_key_levels)
    res_score, res_state = l2[0],l2[1]

    for i in range(len(support_key_levels)):
        support_key_levels[i].append(sup_state[i])
    
    for i in range(len(resistance_key_levels)):
        resistance_key_levels[i].append(res_state[i])

    column_names = ['Call_OI', 'Call_change_in_OI','Call_total_traded_vol', 'Call_net_change', 'StrikePrice', 'Put_net_change', 'Put_total_traded_vol', 'Put_change_in_OI', 'Put_OI', 'Trend']
    support_peaks = pd.DataFrame(support_key_levels, columns = column_names )
    resistance_peaks = pd.DataFrame(resistance_key_levels, columns = column_names)   

    supp_keys = get_req_keys(support_peaks, spotprice, True)
    res_keys = get_req_keys(resistance_peaks, spotprice, False)

    return {
        'supp-levels' : supp_keys,
        'res-levels' : res_keys 
    }
    
if __name__ == "__main__":
    app.run()

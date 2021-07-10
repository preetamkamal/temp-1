# from Project.fetch_option_chain import get_underlying_asset_value
# from Project.main import get_req_keys
from flask import Flask, render_template, request
from fetch_option_chain import * 
from main import *
from api_details import *

# print(__name__)
app = Flask(__name__, static_folder='static/',
static_url_path='',
template_folder='templates/')

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('frontend.html')

@app.route('/intra-day', methods=['GET'])
def intra_day():
    real_time_data = fetch_json('NIFTY', "nse")
    spotprice = get_underlying_asset_value(real_time_data)
    dates = get_expiry_dates(real_time_data)

    support_key_levels, resistance_key_levels = fetch_support_resistance_levels(real_time_data, dates[0], True)
    # req_supp_levels = get_req_keys(support_key_levels, spotprice, False)
    # req_res_levels = get_req_keys(resistance_key_levels, spotprice, True)
    result = dict()
    result['supp-levels'] = support_key_levels
    result['res-levels'] = resistance_key_levels
    
    return result


# @app.route('/weekly', methods=['GET'])
# def intra_day():
#     real_time_data = fetch_json('NIFTY', "nse")
#     dates = get_expiry_dates(real_time_data)


if __name__ == "__main__":
    app.run(debug=True)

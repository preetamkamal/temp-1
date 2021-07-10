from fetch_option_chain import *
import pandas as pd

def is_peak(df, i, col):
    return ((df[col][i] > df[col][i-1])  or (df[col][i] > df[col][i+1]))

def get_peaks(df, col1, INTRA_DAY, col2):
    
    if INTRA_DAY:
        col = col2
    else: 
        col = col1

    peaks = list()
    for i in range(2, df.shape[0]-2):
        if is_peak(df, i, col):
            peaks.append(df.iloc[i])
    return pd.DataFrame(peaks, columns = df.columns)

def get_keys(df, spotprice):
    df1 = df[df['StrikePrice']<=spotprice].tail(3)
    df2 = df[df['StrikePrice']>spotprice].head(3)
    df = pd.concat([df1, df2])
    return df.values.tolist()

def get_req_keys(df, spotprice, flag):
    
    if flag:
        #puts
        df = df[df['StrikePrice']<=spotprice].tail(3)
        return df.values.tolist()
    else:
        #calls
        df = df[df['StrikePrice']>spotprice].head(3)
        return df.values.tolist()

'''
Data Format in each 'level' row of levels

['Call_OI', 'Call_change_in_OI','Call_total_traded_vol', 'Call_net_change', 
'StrikePrice', 
'Put_net_change', 'Put_total_traded_vol', 'Put_change_in_OI', 'Put_OI']

# 1 - call OI
# 2 - call_change in oi
# 3 - Call volume
# 4 - call net change
# 5 - strike price
# 6 - put net change
# 7 - put volume
# 8 - put change in oi
# 9 - put OI

'''

def get_supp_num(levels):
    
    level_priority = [0.025, 0.075, 0.4, 0.4, 0.075, 0.025]
    gran = [0.2, 0.2, 0.6]
    score = 0

    state = []

    for level in levels:
        if level[5] >= 0 and level[-2] >= 0:
            # BEARISH
            state.append(-1)
        elif level[5] < 0 and level[-2] >= 0:
            # BULLISH
            state.append(1)
        elif level[5] >=0 and level[-2] < 0:
            # WEAKLY BEARISH
            state.append(-0.5)
        else:
            # WEAKLY BULLISH
            state.append(+0.5)
    for i in range(len(levels)):
        
        level = levels[i]

        level_score = level[6]*gran[0] + level[7]*gran[1] + level[8]*gran[2]
        level_score *= level_priority[i] * state[i]

        score += level_score

    l = []
    l.append(score)
    l.append(state)
    return l


def get_resis_num(levels):
    
    level_priority = [0.025, 0.075, 0.4, 0.4, 0.075, 0.025]
    gran = [0.2, 0.2, 0.6]
    score = 0

    state = []
    values = []

    for level in levels:
        if level[3] >= 0 and level[0] >= 0:
            # BEARISH
            state.append(1)
        elif level[3] < 0 and level[0] >= 0:
            # BULLISH
            state.append(-1)
        elif level[3] >=0 and level[0] < 0:
            # WEAKLY BEARISH
            state.append(+0.5)
        else:
            # WEAKLY BULLISH
            state.append(-0.5)
    
    for i in range(len(levels)):
        
        level = levels[i]

        level_score = level[2]*gran[0] + level[1]*gran[1] + level[0]*gran[2]
        level_score *= level_priority[i] * state[i]

        score += level_score
    l = []
    l.append(score)
    l.append(state)
    return l

def fetch_support_resistance_levels(data, date, INTRA_DAY):
    
    spotprice = get_underlying_asset_value(data)
    data = date_filter(data, date)
    support_peaks = get_peaks(data, 'Put_OI', INTRA_DAY, 'Put_change_in_OI')
    resistance_peaks = get_peaks(data, 'Call_OI', INTRA_DAY, 'Call_change_in_OI')
    support_key_levels  = get_keys(support_peaks, spotprice)
    resistance_key_levels = get_keys(resistance_peaks, spotprice)
    
    return support_key_levels, resistance_key_levels



def get_trend(data, date, INTRA_DAY):

    support_key_levels, resistance_key_levels = fetch_support_resistance_levels(data, date, INTRA_DAY)
    
    snum = get_supp_num(support_key_levels)
    rnum = get_resis_num(resistance_key_levels)

    trend = ''
    
    if (rnum + snum > 0):
        trend = 'Bullish'

    else:
        trend = 'Bearish'

    return 'The current trend of the market is more likely {} [{}].'.format(trend, date)

def get_realtime_trend(INTRA_DAY=True):

    real_time_data = fetch_json('NIFTY', "nse")
    dates = get_expiry_dates(real_time_data)

    if INTRA_DAY:
        # Intra_Day    
        trend = get_trend(real_time_data, dates[0], INTRA_DAY)
    else:
        # Weekly
        print('Weekly trend')
        trend = get_trend(real_time_data, dates[1], INTRA_DAY)

    print(trend)

def test_trend_prediction(json_filename, INTRADAY=True):

    import json
    try:
        with open(json_filename) as file:
            data = json.load(file)
            dates = get_expiry_dates(data)
        if INTRADAY:
            print(get_trend(data, dates[0], INTRADAY))
        else:
            print(get_trend(data, dates[1], INTRADAY))
    except:
        print('An ERROR has occurred while handling the FILE')


if __name__ == "__main__":
    get_realtime_trend()
    # test_trend_prediction('<file_name>.json')
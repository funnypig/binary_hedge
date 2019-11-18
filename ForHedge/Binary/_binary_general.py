
'''
    There is general information about using BinaryAPI and authorization details.

    Global const variables:
        APP_ID
        API_URL

    For more information visit https://developers.binary.com/api/
'''

import json

APP_ID = 19182

API_URL = 'wss://ws.binaryws.com/websockets/v3?app_id='

def get_binary_url(appid=None):

    return API_URL + str(APP_ID) if appid is None else str(appid)

# API CALL PATTERNS

# UNAUTHORIZED:

ASSETS_PATTERN = {
    "asset_index": 1,
    "req_id": 0
}

def get_asset_json(req_id=0):
    req = ASSETS_PATTERN.copy()
    req['req_id'] = req_id

    return json.dumps(req)


FORGET_STREAM_PATTERN = {
    "forget": "streamID",
    "req_id": 0
}

def get_forget_stream_json(streamID, req_id=0):
    req = FORGET_STREAM_PATTERN.copy()
    req['forget'] = streamID
    req['req_id'] = req_id

    return json.dumps(req)


# FORGET ALL SPECIFIED STREAMS: candles, ticks, proposal...
FORGET_ALL_PATTERN = {
    "forget_all": "ticks",
    "req_id": 0
}

def get_forget_all_json(stream_name, req_id=0):
    req = FORGET_ALL_PATTERN.copy()
    req['forget_all'] = stream_name
    req['req_id'] = req_id

    return json.dumps(req)


PING_PATTERN = {
    "ping": 1,
    "req_id": 0
}

def get_ping_json(req_id=0):
    req = PING_PATTERN.copy()
    req['req_id'] = req_id

    return json.dumps(req)


PRICE_PROPOSAL_PATTERN = {
    "proposal": 1,
    "amount": 100,
    "basis": "stake",
    "contract_type": "CALL",
    "currency": "USD",
    "duration": 60,
    "duration_unit": "s",
    "symbol": "R_100",
    "req_id": 0
}

def get_price_proposal_json(amount=100, type='CALL', duration=60,
                            duration_unit='s', symbol='frxEURUSD', req_id=0):
    req = PRICE_PROPOSAL_PATTERN.copy()
    req['amount'] = amount
    req['contract_type'] = type
    req['duration'] = duration
    req['duration_unit'] = duration_unit
    req['symbol'] = symbol
    req['req_id'] = req_id

    return json.dumps(req)


def get_price_proposal_dict(amount=100, type='CALL', duration=60,
                            duration_unit='s', symbol='frxEURUSD'):
    req = PRICE_PROPOSAL_PATTERN.copy()
    req['amount'] = amount
    req['contract_type'] = type
    req['duration'] = duration
    req['duration_unit'] = duration_unit
    req['symbol'] = symbol

    req.pop('req_id')
    req.pop('proposal')

    return req

TICK_STREAM_PATTERN = {
    "ticks": "frxEURUSD",
    "subscribe": 1,
    "req_id": 0
}

def get_tick_stream_json(symbol='frxEURUSD', subscribe=1, req_id=0):
    req = TICK_STREAM_PATTERN.copy()
    req['ticks'] = symbol
    req['req_id'] = req_id
    if subscribe != 1:
        req.pop('subscribe')

    return json.dumps(req)


TICK_HISTORY_PATTERN = {
    "ticks_history": "R_50",
    "end": "latest",
    "start": 1,
    "style": "candles",
    "adjust_start_time": 1,
    "granularity":60,
    "subscribe":1,
    "count": 10,
    "req_id": 0
}

def get_tick_history_json(symbol='frxEURUSD', start=1, end='latest',
                          style='candles', granularity=60, count=10,
                          subscribe=1, req_id=0):

    req = TICK_HISTORY_PATTERN.copy()
    req['ticks_history'] = symbol
    req['end'] = end
    req['start'] = start
    req['style'] = style
    if style!='candles':
        req.pop('granularity')
    else:
        req['granularity'] = granularity
    req['count'] = count
    if subscribe!=1:
        req.pop('subscribe')
    req['req_id'] = req_id

    return json.dumps(req)



# ONLY FOR AUTHORIZED:

AUTHORIZE_PATTERN = {
    "authorize": "apiToken",
    "req_id" : 0
}

def get_authorize_json(apiToken, req_id=0):
    req = AUTHORIZE_PATTERN.copy()
    req['authorize'] = apiToken
    req['req_id'] = req_id

    return json.dumps(req)


LOGOUT_PATTERN = {
    "logout": 1,
    "req_id": 0
}

def get_logout_json(req_id=0):
    req = LOGOUT_PATTERN.copy()
    req['req_id'] = req

    return json.dumps(req)


BALANCE_PATTERN = {
    "balance": 1,
    "subscribe": 0,
    "account": "current",
    "req_id": 0
}

def get_balance_json(subscribe=0, req_id=0):
    req = BALANCE_PATTERN.copy()
    req['subscribe'] = subscribe
    req['req_id'] = req_id

    return json.dumps(req)


LOGIN_HISTORY_PATTERN = {
    "login_history": 1,
    "limit": 25,
    "req_id": 0
}

def get_login_history_json(limit=25, req_id=0):
    req = LOGIN_HISTORY_PATTERN.copy()
    req['limit'] = limit
    req['req_id'] = req_id

    return json.dumps(req)


# BUY, SELL, DEPOSIT, WITHDRAWAL
STATEMENT_PATTERN = {
    "statement": 1,
    "description": 1,
    "limit": 10,
    "offset": 0,
    "date_from": 0,
    "date_to": 0,
    "req_id": 0
}

def get_statement_json(limit=10, offset=0, date_from=0, date_to=0, req_id=0):
    req = STATEMENT_PATTERN.copy()
    req['limit'] = limit
    req['offset'] = offset
    if date_from == 0 or date_to == 0:
        req.pop('date_from')
        req.pop('date_to')
    else:
        req['date_from'] = date_from
        req['date_to'] = date_to
    req['req_id'] = req_id

    return json.dumps(req)


# CURRENT OPTIONS
PORTFOLIO_PATTERN = {
    "portfolio": 1,
    "req_id": 0
}

def get_portfolio_json(req_id=0):
    req = PORTFOLIO_PATTERN.copy()
    req['req_id'] = req_id

    return json.dumps(req)


CONTRACT_PROPOSAL_PATTERN = {
    "proposal_open_contract": 1,
    "contract_id": 11111111,
    "subscribe": 1,
    "req_id": 0
}

def get_contract_proposal_json(contract_id, subscribe=1, req_id=0):
    req = CONTRACT_PROPOSAL_PATTERN.copy()
    req['contract_id'] = contract_id
    if subscribe!=1:
        req.pop('subscribe')
    req['req_id'] = req_id

    return json.dumps(req)


PROFIT_TABLE_PATTERN = {
    "profit_table": 1,
    "description": 1,
    "limit": 25,
    "offset": 0,
    "date_from": 0,
    "date_to": 0,
    "req_id": 0
}

def get_profit_table_json(limit=25, offset=0, date_from=0, date_to=0, req_id=0):
    req = PROFIT_TABLE_PATTERN.copy()
    req['limit'] = limit
    req['offset'] = offset
    if date_from == 0 or date_to == 0 or date_from is None or date_to is None:
        req.pop('date_from')
        req.pop('date_to')
    else:
        req['date_from'] = date_from
        req['date_to'] = date_to
    req['req_id'] = req_id

    return json.dumps(req)


SELL_CONTRACT_PATTERN = {
    "sell": 11542203588,
    "price": 500,
    "req_id": 0
}

def get_sell_contract_json(contract_id, price=0, req_id=0):
    req = SELL_CONTRACT_PATTERN.copy()
    req['sell'] = contract_id
    req['price'] = price # 0 - sell now
    req['req_id'] = req_id

    return json.dumps(req)


BUY_CONTRACT_PATTERN = {
    "buy": "proposal_ID",
    "price": 100,
    "req_id": 0
}

def get_buy_contract_json(proposal_id, price=1, proposal_parameters=None, req_id=0):
    req = BUY_CONTRACT_PATTERN.copy()
    req['buy'] = proposal_id
    req['price'] = price

    if proposal_id == 1:
        req['parameters'] = proposal_parameters

    req['req_id'] = req_id

    return json.dumps(req)

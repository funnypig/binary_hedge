
'''
    This module gives access to Binary.com account via BinaryAPI by given api token

    You can:
        - authorize
        - get transactions history
        - get current contracts
        - buy/sell contracts

'''

import Binary._binary_general as bin_api
import Binary._multithread_helper as mt_helper
from websocket import WebSocketApp
import json
from threading import Thread, Lock, Event
import logging
import sys
import traceback

class BinaryAccount(mt_helper.MultiThreadWSHelper):
    '''
        Make all operations with binary.com account by given apiToken
        You can:
            - read portfolio
            - read statement
            - buy/sell contracts

        all methods can be called from different threads.

        Each request has unique ID for internal usage.
        And each response has the same ID.
    '''

    def __init__(self, apiToken):

        super().__init__()

        self.apiToken = apiToken
        self.url = bin_api.get_binary_url()
        self.app = WebSocketApp(url=self.url,
                                on_open = lambda ws: self.on_app_open(ws),
                                on_close = lambda ws: self.on_app_close(ws),
                                on_message = lambda ws, msg: self.on_app_msg(ws, msg),
                                on_error = lambda ws, err: self.on_app_error(ws, err),
                                on_ping = lambda ws: self.on_app_ping(ws))

        self.authorized = False

        '''
            If connection closes by any reason, BinaryAccount will create new application.
            If the app is closed and reconnection is not required, it won't.
        '''
        self.reconnect = True


    def send_request(self, request):
        '''
        Sends request considering sharing between threads.
        Ideally it should be placed into helper,
        but app (WebSocketApp) defined here
        '''

        with self.ws_lock:
            self.app.send(request)

    def open_app(self):
        Thread(target=self.app.run_forever).start()
        while not self.authorized:
            pass

    def close_app(self):
        del self.responses
        self.reconnect = False
        self.app.close()

    # Websockets methods:

    def on_app_open(self, ws):

        # Authorize on open
        curID = self.get_next_req_id()
        curEvent = Event()
        self.add_event(curID, curEvent)
        self.send_request(bin_api.get_authorize_json(self.apiToken, req_id=curID))


    def on_app_msg(self, ws, msg):

        try:
            resp = json.loads(msg)
            self.add_response(resp)

            if 'authorize' in resp:
                self.authorized = True

            id_ = resp['req_id']
            if self.in_events(id_):
                self.set_event(id_)

        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))

        ready = True # line for debug

    def on_app_close(self, ws):

        if self.reconnect:
            self.app = WebSocketApp(url=self.url,
                                on_open = lambda ws: self.on_app_open(ws),
                                on_close = lambda ws: self.on_app_close(ws),
                                on_message = lambda ws, msg: self.on_app_msg(ws, msg),
                                on_error = lambda ws, err: self.on_app_error(ws, err),
                                on_ping = lambda ws: self.on_app_ping(ws))
            Thread(target=self.app.run_forever).start()

    def on_app_error(self, ws, error):
        pass

    def on_app_ping(self, ws):
        pass

    # Account manipulation methods

    def get_balance(self):

        try:
            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)
            self.send_request(bin_api.get_balance_json(req_id=curID))

            curEvent.wait()

            response = self.get_response(curID)

            return response['balance']['balance']

        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))


    def get_portfolio(self):
        '''
        Returns current opened positions as list of dict
        Each dict has keys:
            - price
            - payout
            - contract_id
            - contract_type
            - date_start
            - date_end
            - description
            - symbol
        :return: list
        '''

        try:

            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)
            self.send_request(bin_api.get_portfolio_json(req_id=curID))

            curEvent.wait()

            response = self.get_response(curID)

            return [{
                'price' : r['buy_price'],
                'payout' : r['payout'],
                'contract_id' : r['contract_id'],
                'contract_type' : r['contract_type'],
                'date_start' : r['date_start'],
                'date_end' : r['expiry_time'],
                'description' : r['longcode'],
                'symbol' : r['symbol']
            } for r in response['portfolio']['contracts']]

        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))

    def get_login_history(self, limit=25):
        '''
        Returns list of string with description of login
        :param limit: max number of login notes
        :return: list
        '''

        try:

            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)
            self.send_request(bin_api.get_login_history_json(req_id=curID))

            curEvent.wait()

            response = self.get_response(curID)

            return [
                r['environment'] for r in response['login_history']
            ]

        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))

    def get_profit_table(self, limit=10, date_from = None, date_to = None):
        '''
        Returns list of dict.
        Keys:
            - price
            - potential_payout
            - sell_price
            - contract_id
            - description
            - purchase_time
            - sell_time
        :param limit:
        :param date_from: int
        :param date_to: int
        :return:
        '''

        try:

            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)

            self.send_request(bin_api.get_profit_table_json(limit=limit,
                                                        date_from=date_from,
                                                        date_to=date_to,
                                                        req_id=curID))
            curEvent.wait()

            response = self.get_response(curID)

            return [{
                'price' : r['buy_price'],
                'potential_payout' : r['payout'],
                'sell_price' : r['sell_price'],
                'contract_id' : r['contract_id'],
                'purchase_time' : r['purchase_time'],
                'sell_time' : r['sell_time'],
                'description' : r['longcode']
            } for r in response['profit_table']['transactions']]

        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))

    def sell_contract(self, contract_id, price=0):
        '''
        Sells specified contract and shows the result as dict
        Keys:
            - balance_after
            - sold_for
            OR
            - error : err_msg
        :param contract_id:
        :param price:
        :return:
        '''

        try:

            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)
            self.send_request(bin_api.get_sell_contract_json(contract_id, price, req_id=curID))

            curEvent.wait()

            response = self.get_response(curID)

            if not 'error' in response:
                return {
                    'balance_after' : response['sell']['balance_after'],
                    'sold_for' : response['sell']['sold_for']
                }
            else:
                return {
                    'error' : response['error']['message']
                }
        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))

    def buy_contract(self, proposal_id = None,
                     amount = 1, type='CALL', duration=15, duration_unit='m', symbol='frxEURUSD'):
        '''
        Buys contract by proposal_id (the object where all parameters were already passed)
        or by given parameters.
        To use custom parameters proposal_id HAVE TO BE None

        Returns dict with details
        Keys:
            - balance_after
            - buy_price
            - contract_id
            - description
            - payout
            - start_time
        :return: dict
        '''

        try:
            curID = self.get_next_req_id()
            curEvent = Event()
            self.add_event(curID, curEvent)

            if not proposal_id is None:
                self.send_request(bin_api.get_buy_contract_json(proposal_id=proposal_id,
                                                                price=amount,
                                                                proposal_parameters=None,
                                                                req_id=curID))
            else:
                proposal_parameters = bin_api.get_price_proposal_dict(amount=amount,
                                                                      type=type,
                                                                      duration=duration,
                                                                      duration_unit=duration_unit,
                                                                      symbol=symbol)
                self.send_request(bin_api.get_buy_contract_json(proposal_id=1,
                                                                proposal_parameters=proposal_parameters,
                                                                price=amount,
                                                                req_id=curID))

            curEvent.wait()

            response = self.get_response(curID)

            if 'error' in response:
                return {
                    'error' : response['error']['message']
                }
            else:
                return {
                    'balance_after' : response['buy']['balance_after'],
                    'buy_price' : response['buy']['buy_price'],
                    'contract_id' : response['buy']['contract_id'],
                    'description' : response['buy']['longcode'],
                    'payout' : response['buy']['payout'],
                    'start_time' : response['buy']['start_time']
                }
        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))
            print(ex_val)

    def get_price_proposal(self, contract_id, subscribe=0):
        '''
        Returns information about opened position as dict
        Keys:
            - buy_price
            - current_spot
            - entry_spot
            - contract_type
            - symbol
            - is_valid_to_sell
            - profit
            - profit_percentage
            - contract_id
            - description

            - subscription_id
            - req_id

        Last two keys are only available for subscriptions.
        This allows to forget subscription and then remove event
        :return: dict
        '''

        curID = self.get_next_req_id()
        curEvent = Event()
        self.add_event(curID, curEvent)

        self.send_request(bin_api.get_contract_proposal_json(contract_id=contract_id,
                                                             subscribe=subscribe,
                                                             req_id=curID))

        if subscribe == 1:

            saved_response = None

            while True:

                # if subscription had been removed
                if not self.in_events(curID):
                    return

                curEvent.wait(10)
                response = self.get_response(curID)
                resp = response['proposal_open_contract']

                curEvent.clear()

                if response != saved_response:
                    saved_response = response
                    yield {
                        'buy_price' : resp['buy_price'],
                        'current_spot' : resp['current_spot'],
                        'entry_spot' : resp['entry_spot'],
                        'contract_type' : resp['contract_type'],
                        'symbol' : resp['display_name'],
                        'is_valid_to_sell' : resp['is_valid_to_sell'],
                        'profit' : resp['profit'],
                        'profit_percentage' : resp['profit_percentage'],
                        'contract_id' : resp['contract_id'],
                        'description' : resp['longcode'],
                        'subscription_id' : response['subscription']['id'],
                        'req_id' : curID
                    }

        else:

            curEvent.wait()

            response = self.get_response(curID)
            resp = response['proposal_open_contract']

            return {
                'buy_price' : resp['buy_price'],
                'current_spot' : resp['current_spot'],
                'entry_spot' : resp['entry_spot'],
                'contract_type' : resp['contract_type'],
                'symbol' : resp['display_name'],
                'is_valid_to_sell' : resp['is_valid_to_sell'],
                'profit' : resp['profit'],
                'profit_percentage' : resp['profit_percentage'],
                'contract_id' : resp['contract_id'],
                'description' : resp['longcode']
            }

    def forget_subscription(self, subscription_id, event_to_remove = None):
        '''
        Makes request to stop receive events by subscription
        :return:
        '''

        curID = self.get_next_req_id()
        curEvent = Event()
        self.add_event(curID, curEvent)
        self.send_request(bin_api.get_forget_stream_json(subscription_id, req_id=curID))

        curEvent.wait()

        if not event_to_remove is None:
            self.remove_event(event_to_remove)




if __name__ == '__main__':

    import time

    acc = BinaryAccount('KKwE587aBEGkt3Z')
    acc.open_app()

    time.sleep(3)

    bal = Thread(target=lambda x: print(x.get_balance()), args=(acc,))
    portfolio = Thread(target=lambda x: print(x.get_portfolio()), args=(acc,))
    profit = Thread(target=lambda x: print(x.get_profit_table()), args=(acc,))
    login = Thread(target=lambda x: print(x.get_login_history()), args=(acc,))

    bal.start()
    bal.join(5)

    '''
    buy_put = acc.buy_contract(amount=256, type='PUT', duration=30, duration_unit='m', symbol='R_100')
    buy_call = acc.buy_contract(amount=256, type='CALL', duration=30, duration_unit='m', symbol='R_100')
    print(buy_put)
    print(buy_call)
    time.sleep(5)
    sell_put = acc.sell_contract(contract_id=buy_put['contract_id'])
    print(sell_put)
    '''

    buy_put = acc.buy_contract(amount=256, type='PUT', duration=30, duration_unit='m', symbol='R_100')
    exit()

    counter = 5
    for price in acc.get_price_proposal('60518963368', subscribe=1):
        print(price)
        time.sleep(0.5)
        counter-=1

        if counter == 0:
            acc.forget_subscription(price['subscription_id'], event_to_remove=price['req_id'])

    print('Finish')

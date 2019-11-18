
import Binary._binary_general as bin_api
import Binary._multithread_helper as mt_helper
from websocket import WebSocketApp
import json
from threading import Thread, Event
import logging
import sys
import traceback

class Binary(mt_helper.MultiThreadWSHelper):
    '''
    Wrapper of Binary.com API
    Provides unathorized operations. Authorized scope is in binary_account module
    '''

    def __init__(self, ):

        super().__init__()
        self.url = bin_api.get_binary_url()
        self.app = WebSocketApp(url=self.url,
                                on_open = lambda ws: self.on_app_open(ws),
                                on_close = lambda ws: self.on_app_close(ws),
                                on_message = lambda ws, msg: self.on_app_msg(ws, msg),
                                on_error = lambda ws, err: self.on_app_error(ws, err),
                                on_ping = lambda ws: self.on_app_ping(ws))

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

    def close_app(self):
        del self.responses
        self.reconnect = False
        self.app.close()

    # Websockets methods:

    def on_app_open(self):
        '''
        We have nothing to do here
        :return:
        '''
        pass


    def on_app_msg(self, ws, msg):

        try:
            resp = json.loads(msg)
            self.add_response(resp)

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

    def get_history(self, asset = 'frxEURUSD', granularity=3600,
                    count=50, subscribe=0, style='candles'):
        '''
        Returns list of candles as tuple:
        tuple = (date, open, high, low, close, subscription_id)
        :return: list
        '''

        curID = self.get_next_req_id()
        curEvent = Event()
        self.add_event(curID, curEvent)
        self.send_request(bin_api.get_tick_history_json(symbol=asset,
                                                        style=style,
                                                        granularity=granularity,
                                                        count=count,
                                                        subscribe=subscribe,
                                                        req_id=curID))

        # TODO: subscribe

        curEvent.wait()

        response = self.get_response(curID)
        response = response['candles']
        return [(r['epoch'], r['open'], r['high'], r['low'], r['close'])
                    for r in response
            ]

    def get_price_proposal(self, asset = 'frxEURUSD', amount = 1,
                          duration = 60, duration_unit = 'm', type='CALL'):
        '''
        Returns price proposal for buying an option as dict
        Keys:
            - date_start
            - proposal_id
            - description
            - payout

        :return: dict
        '''

        curID = self.get_next_req_id()
        curEvent = Event()
        self.add_event(curID, curEvent)
        self.send_request(bin_api.get_price_proposal_json(amount=amount,
                                                          type=type,
                                                          duration=duration,
                                                          duration_unit=duration_unit,
                                                          symbol=asset,
                                                          req_id=curID))

        curEvent.wait()

        response = self.get_response(curID)
        if 'error' in response:
            return {
                'date_start' : '',
                'proposal_id' : '',
                'description' : response['error']['message'],
                'payout' : 0,
                'error' : True,
                'err_msg' : response['error']['message']
            }

        return {
            'date_start' : response['proposal']['date_start'] if 'date_start' in response['proposal'] else '',
            'proposal_id' : response['proposal']['id'],
            'description' : response['proposal']['longcode'],
            'payout' : response['proposal']['payout'],
            'error' : False,
            'err_msg' : ''
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


import socket
from threading import Event, Lock, Thread
import re
import sys
import traceback
import logging

# FUNCTIONS TO PROCESS RESPONSE FROM MetaTrader
RE_GET_SYMBOL = re.compile(r'Symbol: [A-Z]{6}')
RE_GET_DEAL_TYPE = re.compile(r'Deal type: [A-Z_]+')
RE_ORDER_ID = re.compile(r'Order ticket: \d+')
RE_PRICE = re.compile(r'Price: \d+\.?\d*')
RE_TAKE_PROFIT = re.compile(r'Take Profit: \d+\.?\d*')
RE_STOP_LOSS = re.compile(r'Stop Loss: \d+\.?\d*')
RE_VOLUME = re.compile(r'Volume: \d+\.\d+')

def get_symbol(s):
    return RE_GET_SYMBOL.findall(s)[0].split(':')[1].strip()
def get_deal_type(s):
    return 'BUY' if 'BUY' in RE_GET_DEAL_TYPE.findall(s)[0].split(':')[1] else 'SELL'
def get_order_id(s):
    return RE_ORDER_ID.findall(s)[0].split(':')[1].strip()
def get_price(s):
    return float(RE_PRICE.findall(s)[0].split(':')[1])
def get_stoploss(s):
    return float(RE_STOP_LOSS.findall(s)[0].split(':')[1])
def get_takeprofit(s):
    return float(RE_TAKE_PROFIT.findall(s)[0].split(':')[1])
def get_volume(s):
    return float(RE_VOLUME.findall(s)[0].split(':')[1])


class MetaTraderAccount:
    '''
    Class to connect with MetaTrader expert and receive opened orders
    '''
    def __init__(self, host = '', port = 64500, event_listener = None):

        self.host = host
        self.port = port                        # connection info

        self.events = []
        self.unread_events = []                 # account events
        self.event_listener = event_listener    # report about new message
        self.unread_events_locker = Lock()
        self.events_locker = Lock()             # synchronize access to events
        '''
            Each event is dict with following keys:
                - symbol
                - type
                - price
                - take_profit
                - stop_loss
                - volume
                - order_id
        '''

        self.connection_alive = True
        self.connected = False
        self.connection_error = False
        self.mt_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def add_event(self, event):
        '''
            Adds new event
        :param event: dict with order parameters
        :return:
        '''
        with self.events_locker:
            self.events.append(event)

    def get_events(self):
        '''
        :return: all the events as list of dict
        '''
        with self.events_locker:
            return self.events.copy()

    def is_unread_events(self):
        '''
        :return: True if there is new order event
        '''
        with self.unread_events_locker:
            return len(self.unread_events)>0

    def add_unread_event(self, event):
        '''
            Adds new order event
        :param event: dict with order parameters
        :return:
        '''
        with self.unread_events_locker:
            self.unread_events.append(event)

    def get_unread_event(self):
        '''
        :return: order which has not been read yet
        '''
        with self.unread_events_locker:
            return self.unread_events.pop()

    def start_connection(self):
        '''
            start server to receive order signals
        :return:
        '''
        self.connection_thread = Thread(target=self.server)
        self.connection_thread.start()

    def kill(self):

        self.connection_alive = False
        self.mt_connection.close()

    def server(self):

        try:
            self.mt_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mt_connection.bind((self.host, self.port))
            self.mt_connection.listen()
        except OSError:
            # fails if port is busy
            self.connection_alive = False
            self.connection_error = True
            return

        # reached if connection
        self.connected = True

        while self.connection_alive:
            try:

                self.mt_connection.settimeout(10)
                conn, addr = self.mt_connection.accept()
                print('Connected')

                with conn:

                    while self.connection_alive:

                        try:
                            # receive data or get Timeout error
                            data = conn.recv(2048).decode(encoding='utf-8')

                            # there was problem with receiving empty lines.
                            if len(data)<5:
                                continue
                            else:
                                break
                        except socket.timeout:
                            continue

                    # parse received data and emit signal if it is ok
                    data = self.process_event(data)
                    if not data is None:
                        self.add_event(data)
                        self.add_unread_event(data)
                        if not self.event_listener is None:
                            self.event_listener.emit(data)

                    # as orders not coming one by one, no need to keep connection alive
                    conn.close()
            except socket.timeout:
                pass

        self.mt_connection.close()

    def process_event(self, string):
        '''
        Returns dict that will be added as event;
        Input string:

            TRADE_TRANSACTION_ORDER_ADD
            Symbol: EURUSD
            Deal ticket: 0
            Deal type: DEAL_TYPE_BUY
            Order ticket: 121955026
            Order type: ORDER_TYPE_BUY_LIMIT
            Order state: ORDER_STATE_STARTED
            Order time type: ORDER_TIME_GTC
            Order expiration: 1970.01.01 00:00
            Price: 1.10191
            Price trigger: 0
            Stop Loss: 0
            Take Profit: 0
            Volume: 0.01
            Position: 0
            Position by: 0

        :param string:
        :return: dict with order params
        '''

        try:
            return {
                'symbol' : 'frx'+get_symbol(string),
                'type' : get_deal_type(string),
                'order_id' : get_order_id(string),
                'price' : get_price(string),
                'stop_loss' : get_stoploss(string),
                'take_profit' : get_takeprofit(string),
                'volume' : get_volume(string)
            }

        except:
            type, val, tb = sys.exc_info()
            logging.error('Unexpected response from MetaTrader:\n'+string)
            logging.error('\n'.join(traceback.format_tb(tb)))



def test_process_event():

    t1 = '''
    TRADE_TRANSACTION_ORDER_ADD
            Symbol: EURUSD
            Deal ticket: 0
            Deal type: DEAL_TYPE_BUY
            Order ticket: 121955026
            Order type: ORDER_TYPE_BUY_LIMIT
            Order state: ORDER_STATE_STARTED
            Order time type: ORDER_TIME_GTC
            Order expiration: 1970.01.01 00:00
            Price: 1.10191
            Price trigger: 0
            Stop Loss: 0
            Take Profit: 0
            Volume: 0.01
            Position: 0
            Position by: 0'''
    t2 = \
    '''
    TRADE_TRANSACTION_ORDER_ADD
    Symbol: EURUSD
    Deal ticket: 0
    Deal type: DEAL_TYPE_BUY
    Order ticket: 134270089
    Order type: ORDER_TYPE_BUY
    Order state: ORDER_STATE_STARTED
    Order time type: ORDER_TIME_GTC
    Order expiration: 1970.01.01 00:00
    Price: 0
    Price trigger: 0
    Stop Loss: 1.11517
    Take Profit: 1.11561
    Volume: 0.02
    Position: 0
    Position by: 0
    '''

    mt = MetaTraderAccount()
    print(mt.process_event(t1))
    print()
    print(mt.process_event(t2))

if __name__ == '__main__':

    # small test is here

    import time
    def test():
        test_process_event()
        exit()

    server = MetaTraderAccount(host='',port=64500)
    server.start_connection()

    while True:
        while server.is_unread_events():
            print(server.get_unread_event())

        time.sleep(1)

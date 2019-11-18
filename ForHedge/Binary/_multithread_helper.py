
from threading import Thread, Lock, Event


class MultiThreadWSHelper:
    '''
        This class helps to manage shared variables between a lot of threads.
        It helps to send, receive and identify requests and responses.

    '''
    def __init__(self):


        '''
            save responses in dictionary, where
            key - request id
            value - response
        '''
        self.responses = dict()

        # use to identify requests
        self.request_id = 0

        '''
            Uses to wait for specified response
            key - request id
            value - Event object
        '''
        self.events = dict()

        # use to share 'responses' and 'request_id' and 'events' between threads
        self.lock_get_next_req_id = Lock()
        self.lock_responses_operations = Lock()
        self.lock_events = Lock()
        self.ws_lock = Lock()


    def get_next_req_id(self):
        '''
        Generates unique request id
        :return: int
        '''

        with self.lock_get_next_req_id:
            id_to_return  = self.request_id
            self.request_id+=1

        return id_to_return

    def in_response(self, id):
        '''
        Checks if specified request is already have been processed
        :param id:
        :return: bool
        '''

        with self.lock_responses_operations:
            value = id in self.responses

        return value

    def add_response(self, response):
        '''
        Adds response to response dict
        :param response: dict
        :return: None
        '''

        with self.lock_responses_operations:
            self.responses[response['req_id']] = response

    def get_response(self, id):
        '''
        Returns specified response
        :param id: int
        :return: dict
        '''

        self.lock_responses_operations.acquire()
        value = self.responses[id]
        self.lock_responses_operations.release()
        return value

    def add_event(self, id, event):
        '''
        Adds events to self.events
        :param id: int
        :return: None
        '''
        with self.lock_events:
            self.events[id] = event

    def remove_event(self, id):
        '''
        Removes event from events by id
        :param id: int
        :return:
        '''

        with self.lock_events:
            self.events.pop(id)

    def set_event(self, id):
        '''
        Notify that specified event is finished -> response has been taken
        :param id: int
        :return:
        '''

        with self.lock_events:
            self.events[id].set()

    def in_events(self, id):
        '''
        Check if id is in event
        :param id: int
        :return:
        '''

        with self.lock_events:
            value = id in self.events

        return value

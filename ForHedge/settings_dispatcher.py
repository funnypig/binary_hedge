
import pickle
import os
from threading import Lock

class SettingsDispatcher:
    '''
    Allows to update, get and set parameters for all widgets from one place.
    '''
    def __init__(self, file_path = 'options.pickle'):

        self.file_path = file_path

        if os.path.exists(file_path):
            with open(self.file_path, 'rb') as file:
                self.settings = pickle.load(file)
        else:
            self.settings = dict()

        self.thread_lock = Lock()

    def save(self):

        with self.thread_lock:
            with open(self.file_path, 'wb') as file:
                pickle.dump(self.settings, file)

    def get_params(self):
        with self.thread_lock:
            return self.settings.keys()

    def is_param(self, param):
        with self.thread_lock:
            return param in self.settings.keys()

    def set_value(self, key, value):

        with self.thread_lock:
            self.settings[key] = value

    def get_value(self, key):

        with self.thread_lock:
            return self.settings[key] if key in self.settings else None

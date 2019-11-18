
'''
    Widget that allows to:
        - start monitoring orders from MetaTrader
        - look at orders as soon as it appears
        - switch on/off hedging received orders
        - hedging received orders is implemented here
'''

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread
from GUI import _common_features
from MetaTrader.mt_account import MetaTraderAccount
from datetime import datetime
from Binary import binary_account

class TransactionListener(QThread):
    '''
        Class which allows to receive signals from connected function that returns dict
    '''
    transaction_updated = QtCore.pyqtSignal(dict)

class MTWindow(QWidget):
    '''

    '''
    def __init__(self, settings_dispatcher):
        '''
            Initializes local variables
        :param settings_dispatcher: global settings dispatcher
        '''

        super().__init__()

        self.client = None                              #
        self.client_thread = None
        self.last_transaction = ''
        self.monitoring_flag = False
        self.settings_dispatcher = settings_dispatcher
        self.mt_listener = None

        _common_features.init_styles(self)
        self.init_widgets()

    def init_widgets(self):
        label_stylesheet = self.settings_dispatcher.get_value('label_stylesheet')   \
                            if self.settings_dispatcher.is_param('label_stylesheet')\
                            else self.label_style_sheet

        table_stylesheet = self.settings_dispatcher.get_value('table_stylesheet')   \
                            if self.settings_dispatcher.is_param('table_stylesheet')\
                            else self.table_stylesheet

        self.monitoring_button_stylesheet_OFF = '''
            QPushButton{
                background-color : #f71857;
                
                font-size : 18px;
                font-family : Roboto;
                font-style : bold;
                border-style : solid;
                border-color : #dadada;
                border-width : 1px;
                border-radius : 2px;
            }
            QPushButton:hover{
                font-size : 20px;
                background-color : #e81551;
            }
            QPushButton:pressed{
                font-size : 24px;
                background-color : #d4144a;
            }
        '''
        self.monitoring_button_stylesheet_ON = '''
            QPushButton{
                background-color : #13c585;
                
                font-size : 18px;
                font-family : Roboto;
                font-style : bold;
                border-style : solid;
                border-color : #dadada;
                border-width : 1px;
                border-radius : 2px;
            }
            QPushButton:hover{
                font-size : 20px;
                background-color : #10af75;
            }
            QPushButton:pressed{
                font-size : 24px;
                background-color : #0e9d69;
            }
        '''

        self.vbox = QVBoxLayout()

        head_label = QLabel('MT5 Transactions Monitoring')
        head_label.setStyleSheet(self.settings_dispatcher.get_value('head_label_stylesheet')
                                 if self.settings_dispatcher.is_param('head_label_stylesheet')
                                 else self.head_label_stylesheet)
        self.vbox.addWidget(head_label)
        #--------------------------------------------------------------------------------------

        second_row = QGridLayout()

        self.transaction_checker = QCheckBox('Hedge transactions')
        self.transaction_checker.setStyleSheet(self.checkbox_stylesheet)
        second_row.addWidget(self.transaction_checker, 0, 0)

        self.monitoring_button = QPushButton('Monitoring')
        self.monitoring_button.setStyleSheet(self.monitoring_button_stylesheet_OFF)
        self.monitoring_button.setToolTip('Click to START monitoring')
        self.monitoring_button.clicked.connect(self.monitoring_button_clicked)
        second_row.addWidget(self.monitoring_button, 0, 1)

        self.vbox.addLayout(second_row, 1)

        #--------------------------------------------------------------------------------------

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            'Rcv Time', 'Asset', 'Type', 'Price', 'Volume', 'Take profit', 'Stop loss', 'Binary Hedge'
        ])

        self.transactions_table.horizontalHeader().setStyleSheet(label_stylesheet)
        self.transactions_table.setStyleSheet(table_stylesheet)

        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.transactions_table.resizeColumnsToContents()
        self.transactions_table.setAutoScroll(True)

        self.vbox.addWidget(self.transactions_table, 2)

        #--------------------------------------------------------------------------------------
        self.vbox.setStretch(0, 1)
        self.vbox.setContentsMargins(2,2,2,2)
        self.vbox.setAlignment(Qt.AlignTop)
        self.setLayout(self.vbox)


    def monitoring_button_clicked(self):
        '''
            Start monitoring orders from MetaTrader or show message about connection error
        :return:
        '''

        # START MONITORING
        self.transaction_listener = TransactionListener()
        self.transaction_listener.transaction_updated.connect(self.transaction_recieved)

        self.mt_listener = MetaTraderAccount(event_listener=self.transaction_listener.transaction_updated,
                                             host=self.settings_dispatcher.get_value('mt_host'),
                                             port=self.settings_dispatcher.get_value('mt_port'))
        self.mt_listener.start_connection()

        while not self.mt_listener.connected:
            if self.mt_listener.connection_error:
                QMessageBox.warning(self, "Error", "Connection error. Try another port")
                return

        # reached when server started successfully
        self.set_monitor_button_on()
        self.monitoring_button.setText("Monitoring: {}:{}".format(self.mt_listener.host, self.mt_listener.port))
        self.monitoring_button.setEnabled(False)

    def set_monitor_button_on(self):
        '''
            Changes design of Monitoring button when Monitoring is disabled
        :return:
        '''
        self.monitoring_button.setToolTip('Click to STOP monitoring')
        self.monitoring_button.setStyleSheet(self.monitoring_button_stylesheet_ON)

    def set_monitor_button_off(self):
        '''
            Changes design of Monitoring button when Monitoring is enabled
        :return:
        '''
        self.monitoring_button.setToolTip('Click to START monitoring')
        self.monitoring_button.setStyleSheet(self.monitoring_button_stylesheet_OFF)

    def transaction_recieved(self, t):
        '''
            Processing received order event.
            Showing it in the table
            Hedging position if option is enabled
        :param t: dict returned by mt_account after receiving order event
        :return:
        '''
        try:
            if self.transaction_checker.isChecked():

                # get parameters which allows to buy an option at binary.com
                token = self.settings_dispatcher.get_value('api_token')     \
                        if self.settings_dispatcher.is_param('api_token')   \
                        else ''

                hedge_amount = self.settings_dispatcher.get_value('hedge_amount')     \
                        if self.settings_dispatcher.is_param('hedge_amount')   \
                        else 0

                hedge_time = self.settings_dispatcher.get_value('hedge_time')     \
                        if self.settings_dispatcher.is_param('hedge_time')   \
                        else 0

                # check parameters. if ok - buy option
                if token == '':
                    msg = 'Enter token to enable hedging'
                elif hedge_amount == 0:
                    msg = 'Enter token to enable hedging'
                elif hedge_time == 0:
                    msg = 'Enter token to enable hedging'
                else:
                    # connect to binary account
                    bin_acc = binary_account.BinaryAccount(token)
                    bin_acc.open_app()

                    # buy option in opposite direction
                    resp = bin_acc.buy_contract(
                        amount=hedge_amount,
                        duration=hedge_time,
                        duration_unit='m',
                        symbol=t['symbol'],
                        type='CALL' if t['type']=='SELL' else 'PUT'
                    )

                    # show result of try
                    msg = resp['description'] if not 'error' in resp else resp['error']
                    bin_acc.close_app()
            else:
                msg = 'Hedging Not Checked'
        except Exception as e:
            msg = str(e)

        self.transactions_table.insertRow(0)

        self.transactions_table.setItem(0, 0, QTableWidgetItem(datetime.now().strftime("%d.%m %H:%M:%S")))
        self.transactions_table.setItem(0, 1, QTableWidgetItem(t['symbol']))
        self.transactions_table.setItem(0, 2, QTableWidgetItem(t['type']))
        self.transactions_table.setItem(0, 3, QTableWidgetItem(str(t['price'])))
        self.transactions_table.setItem(0, 4, QTableWidgetItem(str(t['volume'])))
        self.transactions_table.setItem(0, 5, QTableWidgetItem(str(t['take_profit'])))
        self.transactions_table.setItem(0, 6, QTableWidgetItem(str(t['stop_loss'])))
        self.transactions_table.setItem(0, 7, QTableWidgetItem(msg))

        self.transactions_table.resizeColumnsToContents()

    def close_(self):
        '''
        Close connection
        :return:
        '''
        if not self.mt_listener is None:
            self.mt_listener.connection_alive = False
            self.mt_listener.kill()

        self.close()

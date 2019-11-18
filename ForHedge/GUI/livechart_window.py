from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import  QIcon
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_finance import candlestick_ohlc

import time
from datetime import datetime
import re
import logging
import traceback
from Binary.binary import Binary
from Binary.binary_account import BinaryAccount

import GUI._common_features as _common_features

class PriceDispatcher(QtCore.QThread):
    '''
    Provides updating prices in real time
    '''

    price_updated = QtCore.pyqtSignal(list)
    price_proposal_updated = QtCore.pyqtSignal(float, float, str, str, bool, str, bool, str)

    def __init__(self, asset, duration, amount):
        super(PriceDispatcher, self).__init__()

        self.asset = asset
        self.duration = duration
        self.amount = amount

        self.last_proposal_update = 0

        self.killed = False

    def get_granularity(self):
        '''
            Calculates granularity in seconds by given duration string
        :return:
        '''
        duration = self.duration

        secs = 1
        if 'm' in duration:
            secs = 60
        if 'h' in duration:
            secs = 60*60
        if 'd' in duration:
            secs = 60*60*24

        sec_count = int(re.findall('\d+', duration)[0])

        return secs*sec_count

    def stop(self):
        '''
        Stops updating price
        :return:
        '''
        self.killed = True

    def run(self):
        # Forex assets starts with 'frx' prefix
        if not self.asset.startswith('frx'):
            self.asset = 'frx' + self.asset
            # Volatility Indices are not started with 'frx'
            if 'VOL100' in self.asset:
                self.asset = 'R_100'

        # init connection with Binary.com
        binary = Binary()
        binary.open_app()
        time.sleep(1) # SORRY FOR THIS

        while not self.killed:
            try:
                # get history of prices
                price = binary.get_history(asset=self.asset,
                                          granularity=self.get_granularity(),
                                          count=20,
                                          subscribe=0,
                                          style='candles')

                # send signal about updated price
                self.price_updated.emit(price)

                # update proposal. but not too fast or Binary wont response
                if time.time()-self.last_proposal_update>1.5:
                    # send requests to get proposals for given asset
                    proposal_up = binary.get_price_proposal(asset=self.asset, amount=self.amount, type='CALL',
                                                            duration=self.get_granularity()//60, duration_unit='m')
                    proposal_down = binary.get_price_proposal(asset=self.asset, amount=self.amount, type='PUT',
                                                            duration=self.get_granularity()//60, duration_unit='m')

                    self.price_proposal_updated.emit(proposal_up['payout'], proposal_down['payout'],
                                                     proposal_up['proposal_id'], proposal_down['proposal_id'],
                                                     proposal_up['error'], proposal_up['err_msg'],
                                                     proposal_down['error'], proposal_down['err_msg'],
                                                     )
                    # save update time
                    self.last_proposal_update = time.time()

                # IT'S ENOUGH TO GET FRESH RESULTS AND NOT OVERLOAD COMPUTER AND SERVER
                time.sleep(0.8)

            except:
                ex_type, ex_val, ex_tb = sys.exc_info()
                logging.error(str(ex_type)+'\n'+'\n'.join(traceback.format_tb(ex_tb)))
                logging.error(ex_val)

        # close connection when requested
        binary.close_app()

class Chart_window(QWidget):
    '''
    Widget to show history of prices by given asset and timeframe
    History is taken from Binary.com
    '''
    def __init__(self, settings_dispatcher):

        super().__init__()

        self.settings_dispatcher = settings_dispatcher

        self.setWindowTitle('Chart and Trade')

        _common_features.init_styles(self)
        self.initUI()

    def initUI(self):

        cur_params = self.settings_dispatcher.get_params() if not self.settings_dispatcher is None else {}

        line_editor_stylesheet = self.settings_dispatcher.get_value('line_editor_stylesheer')   \
                                if 'line_editor_stylesheer' in cur_params                 \
                                else self.line_edit_stylesheet
        label_stylesheet = self.settings_dispatcher.get_value('label_stylesheet')   \
                            if 'label_stylesheet' in cur_params                     \
                            else self.label_style_sheet
        head_label_stylesheet = self.settings_dispatcher.get_value('head_label_stylesheet') \
                            if 'head_label_stylesheet' in cur_params                        \
                            else self.head_label_stylesheet
        button_stylesheet = self.settings_dispatcher.get_value('button_stylesheet') \
                            if 'button_stylesheet' in cur_params                    \
                            else self.button_stylesheet
        combobox_stylesheet = self.settings_dispatcher.get_value('combobox_stylesheet') \
                            if 'combobox_stylesheet' in cur_params                      \
                            else self.combobox_stylesheet


        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setGeometry(QRect())

        self.asset_box = QComboBox()
        # Some Major Pairs added at this moment
        self.asset_box.addItems(['EURUSD', 'AUDUSD', 'EURJPY', 'USDCAD', 'EURCHF', 'VOL100'])

        self.time_box = QComboBox()
        self.time_box.addItems(['1m', '5m', '15m', '30m', '1h', '4h', '1d'])

        self.asset_box.setStyleSheet(combobox_stylesheet)
        self.asset_box.setAutoFillBackground(True)
        self.time_box.setStyleSheet(combobox_stylesheet)
        self.time_box.setAutoFillBackground(True)

        self.grid = QGridLayout()
        grid = self.grid
        grid.addWidget(self.asset_box, 0, 0)
        grid.addWidget(self.time_box, 0, 1)
        self.vbox.addLayout(grid)

        #--------------------------------------------------------------------------------
        # Toolbar actions

        self.figure = Figure(facecolor='#141523', edgecolor='#141523')
        self.chart_view = FigureCanvas(self.figure)
        self.price_disp = None

        self.ax = self.figure.add_subplot(facecolor='#141523')
        self.ax.tick_params(grid_color='#797987', colors='#797987', bottom=False, labelcolor='w')

        self.ax.grid()
        self.figure.autofmt_xdate()
        self.figure.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
        #self.ax.autoscale(tight=True)

        grid.addWidget(self.chart_view, 1, 0, 1, 2)

        #--------------------------------------------------------------------------------
        # Toolbar actions

        self.toolbar = QToolBar()

        self.start_price = QAction(QIcon('./icons/play.png'), 'Click to start or update asset/duration', self)
        self.start_price.triggered.connect(self.start_updater)

        self.trade_up_button = QAction(QIcon('./icons/up.png'), 'Trade UP', self)
        self.trade_up_button.triggered.connect(self.trade_up)

        self.trade_down_button = QAction(QIcon('./icons/down.png'), 'Trade DOWN', self)
        self.trade_down_button.triggered.connect(self.trade_down)

        self.trade_amount_editor = QLineEdit('amount')
        self.trade_amount_editor.setStyleSheet(line_editor_stylesheet)
        self.trade_amount_editor.setFixedWidth(200)
        self.trade_amount_editor.setToolTip('Trade amount')
        self.trade_amount_editor.textChanged.connect(self.amount_changed)

        self.trade_up_proposal_id = None
        self.trade_down_proposal_id = None

        self.toolbar.addAction(self.start_price)
        self.toolbar.addAction(self.trade_up_button)
        self.toolbar.addWidget(self.trade_amount_editor)
        self.toolbar.addAction(self.trade_down_button)

        self.toolbar.setIconSize(QSize(40, 40))

        self.vbox.addWidget(self.toolbar)

        self.setLayout(self.vbox)

    def trade_up(self):
        '''
        Buy a CALL option with given asset, amount and timeframe
        :return:
        '''
        apiToken = self.settings_dispatcher.get_value('api_token')
        if apiToken is None:
            QMessageBox.information(self, 'Trade failed',"Set 'API token' in Settings window!")
            return

        proposal = self.trade_up_proposal_id
        if proposal is None:
            QMessageBox.information(self, 'Trade failed',"Start chart update to get proposal information")
            return

        amount = self.trade_amount_editor.text()
        try:
            amount = float(amount)
        except:
            QMessageBox.information(self, 'Trade failed',"Set valid amount")
            return

        # if all the parameters are ok - buy an option
        acc = BinaryAccount(apiToken)
        acc.open_app()
        time.sleep(1)

        # get result and show message
        try:
            res = acc.buy_contract(amount=amount, type='CALL', duration=self.price_disp.get_granularity()//60,
                               duration_unit='m', symbol=self.price_disp.asset)

            if 'error' in res:
                QMessageBox.warning(self, "Error", res['error'])
            else:
                QMessageBox.information(self, 'Trade', res['description']+'\nBalance after: ' + \
                                (str(res['balance_after']) if 'balance_after' in res else '-'))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            acc.close_app()

    def trade_down(self):
        '''
        Buy an option
        :return:
        '''
        apiToken = self.settings_dispatcher.get_value('api_token')
        if apiToken is None:
            QMessageBox.information(self, 'Trade failed',"Set 'API token' in Settings window!")
            return

        proposal = self.trade_down_proposal_id
        if proposal is None:
            QMessageBox.information(self, 'Trade failed',"Start chart update to get proposal information")
            return

        amount = self.trade_amount_editor.text()
        try:
            amount = float(amount)
        except:
            QMessageBox.information(self, 'Trade failed',"Set valid amount")
            return

        # if all the parameters are ok - buy an option
        acc = BinaryAccount(apiToken)
        acc.open_app()

        # get result and show message
        try:
            res = acc.buy_contract(amount=amount, type='PUT', duration=self.price_disp.get_granularity()//60,
                               duration_unit='m', symbol=self.price_disp.asset)

            if 'error' in res:
                QMessageBox.warning(self, "Error", res['error'])
            else:
                QMessageBox.information(self, 'Trade', res['description']+'\nBalance after: ' + \
                                (str(res['balance_after']) if 'balance_after' in res else '-'))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        finally:
            acc.close_app()

    def amount_changed(self, text):
        '''
        Update trade amount if it is float or clear input field
        :param text: str
        :return:
        '''
        if not self.price_disp is None:
            try:
                amount = float(text)
                self.price_disp.amount = amount
            except:
                self.trade_amount_editor.clear()

    def start_updater(self):

        # Init chart widgets and start price dispatcher (updater)
        self.grid.removeWidget(self.chart_view)

        self.figure = Figure(figsize=(20,15), facecolor='#141523', edgecolor='#141523')
        self.chart_view = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(facecolor='#141523')
        self.ax.tick_params(grid_color='#797987', colors='#797987', bottom=False, labelcolor='w')

        self.ax.grid()
        self.figure.autofmt_xdate()
        self.figure.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)

        self.grid.addWidget(self.chart_view, 1, 0, 1, 2)
        #----------------------------------------------------------------------------------------------

        if not self.price_disp is None:
            self.price_disp.stop()

        try:
            amount = self.trade_amount_editor.text()
            amount = float(amount)
        except:
            amount = 1
            self.trade_amount_editor.setText('1')

        self.price_disp = PriceDispatcher(self.asset_box.currentText(), self.time_box.currentText(), amount)
        self.price_disp.price_updated.connect(self.update_chart)
        self.price_disp.price_proposal_updated.connect(self.payout_updated)
        self.price_disp.start()

    def stop_updater(self):

        self.price_disp.stop()
        time.sleep(2) # SORRY FOR THIS
        del self.price_disp

        self.price_disp = None

    def payout_updated(self, up, down, up_id, down_id, err_up, err_msg_up, err_down, err_msg_down):
        '''
        Update PAYOUT information on tooltips on Trade buttons
        :param up:
        :param down:
        :param up_id:
        :param down_id:
        :param err_up:
        :param err_msg_up:
        :param err_down:
        :param err_msg_down:
        :return:
        '''
        if err_up:
            self.trade_up_button.setText('Error:\n'+err_msg_up)
        else:
            self.trade_up_button.setText('Trade UP\nPayout: {}'.format(up))
        if err_down:
            self.trade_down_button.setText('Error:\n'+err_msg_down)
        else:
            self.trade_down_button.setText('Trade DOWN\nPayout: {}'.format(down))

        self.trade_up_proposal_id = up_id
        self.trade_down_proposal_id = down_id

    def update_chart(self, candle_data):
        '''
        Redraw chart with new data
        candle_data is list that was returned by binary.get_history
        this is list of tuples :
        tuple = (date, open, high, low, close, subscription_id)

        :param candle_data:
        :return:
        '''

        self.ax.clear()
        self.ax.tick_params(grid_color='#797987', colors='#797987', bottom=False, labelcolor='w')

        self.ax.grid()

        dates = list(map(
            lambda x: datetime.fromtimestamp(x[0]).strftime('%H:%M'),
            candle_data))
        i = 0
        def I():
            nonlocal i
            i+=1
            return i

        candle_data = list(map(lambda x: (I(), x[1], x[2], x[3], x[4]), candle_data))
        candlestick_ohlc(self.ax, candle_data, colorup='#13c585', colordown='#f71857', width=0.3)

        self.ax.set_xticklabels(dates)
        # remove subscription id from tuples

        self.ax.set_xticklabels(dates)
        self.chart_view.draw()

if __name__ == '__main__':

    closes = [1.1128, 1.1075, 1.1033, 1.1029, 1.1042]
    closes.extend(closes)

    opens = [1.1075, 1.1034, 1.1029, 1.1043, 1.1006	]
    opens.extend(opens)

    highs = [1.1139, 1.1085, 1.1047, 1.1049, 1.1064]
    highs.extend(highs)

    lows = [1.1065, 1.1022, 1.0991, 1.1012, 1.1001]
    lows.extend(lows)

    dates = list(range(10))

    data = [
        (dates[i], opens[i], highs[i], lows[i], closes[i]) for i in range(len(closes))
    ]

    import sys

    app = QApplication(sys.argv)
    ex = Chart_window(None)
    ex.setGeometry(50, 50, 600, 400)

    ex.update_chart(data)
    ex.show()
    sys.exit(app.exec_())

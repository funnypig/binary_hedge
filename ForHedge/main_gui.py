
'''
    Main module which creates Main Window and initializes widgets
'''

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import sys

from GUI.livechart_window import Chart_window
from GUI.settings_window import Settings_window
from GUI.metatrader_window import MTWindow

from settings_dispatcher import SettingsDispatcher

SETTINGS_DISPATCHER = SettingsDispatcher()

class Application(QMainWindow):
    '''
    Creates main window and toolbar to navigate through widgets
    '''
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Binary account')

        #
        self.setStyleSheet('''
            background : #141523;
            color : white;
            font-family : "Roboto";
            font-style : oblique;
            font-size : 16px;
        ''')

        self.create_menu()
        self.setGeometry(300, 150, 800, 500)
        self.show()

        # initialize windows
        self.settings_window = Settings_window(SETTINGS_DISPATCHER)
        self.chart_window = Chart_window(SETTINGS_DISPATCHER)
        self.mt_window = MTWindow(SETTINGS_DISPATCHER)

        # need to store widget references
        self.curWidget = None

    def create_menu(self):

        self.toolBar = QToolBar()
        self.toolBar.setIconSize(QSize(50,50))

        # add buttons to navigate through windows

        self.chart_action = QAction(QIcon('./icons/chart.png'), 'Chart', self)
        self.chart_action.triggered.connect(self.open_chart)
        self.toolBar.addAction(self.chart_action)

        self.profit_table_action = QAction(QIcon('./icons/profit_table.png'), 'Profit table', self)
        self.profit_table_action.triggered.connect(self.open_profit_table)
        self.toolBar.addAction(self.profit_table_action)

        self.portfolio_action = QAction(QIcon('./icons/portfolio.png'), 'Portfolio', self)
        self.portfolio_action.triggered.connect(self.open_portfolio)
        self.toolBar.addAction(self.portfolio_action)

        self.statement_action = QAction(QIcon('./icons/statement.png'), 'Statement', self)
        self.statement_action.triggered.connect(self.open_statement)
        self.toolBar.addAction(self.statement_action)

        self.metatrader_action = QAction(QIcon('./icons/mql.png'), 'MetaTrader Account', self)
        self.metatrader_action.triggered.connect(self.open_metatrader_window)
        self.toolBar.addAction(self.metatrader_action)

        self.settings_action = QAction(QIcon('./icons/settings.png'), 'Settings', self)
        self.settings_action.triggered.connect(self.open_settings)
        self.toolBar.addAction(self.settings_action)

        self.close_action = QAction(QIcon('./icons/close.png'), 'Close', self)
        self.close_action.triggered.connect(self.close_app)
        self.toolBar.addAction(self.close_action)

        self.toolBar.setStyleSheet('''
            margin-top: 3px;
            margin-bottom: 3px;
            margin-right: 6px;
            margin-left: 6px;
        ''')
        self.addToolBar(self.toolBar)

    def open_chart(self):
        '''
        Opens LiveChart window to look at prices
        :return:
        '''
        self.curWidget = self.takeCentralWidget()

        self.setWindowTitle('Chart and Trade')
        self.setCentralWidget(self.chart_window)


    def open_settings(self):
        '''
        Opens Settings window - managing settings
        '''
        self.curWidget = self.takeCentralWidget()

        self.setWindowTitle('Settings')
        self.setCentralWidget(self.settings_window)

    def open_profit_table(self):

        pass

    def open_portfolio(self):

        pass

    def open_statement(self):

        pass

    def open_metatrader_window(self):
        '''
        Opens MetaTrader window
        :return:
        '''

        self.curWidget = self.takeCentralWidget()

        self.setWindowTitle('MT5 Account Monitoring')
        self.setCentralWidget(self.mt_window)

    def close_app(self):

        self.close()
        self.chart_window.close()
        self.settings_window.close()
        self.mt_window.close_()
        sys.exit()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())

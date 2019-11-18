from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import GUI._common_features as _common_features

class Settings_window(QWidget):
    '''
    Window which allows to manage current session settings and save settings for the next one
    '''
    def __init__(self, settings_dispatcher):

        super(QWidget, self).__init__()

        self.settings_dispatcher = settings_dispatcher
        self.setWindowTitle('Settings')
        _common_features.init_styles(self)
        self.initUI()

    def initUI(self):
        '''
        Initilizes UI with default application fonts.
        Check of settings is written for future customization
        :return:
        '''

        # save all the params once to not make requests to dispatcher a lot of times
        cur_params = self.settings_dispatcher.get_params()

        # init some design patterns to use after
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


        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignTop)
        lineCounter = 0

        label = QLabel('Settings')
        label.setStyleSheet(head_label_stylesheet)
        self.grid.addWidget(label, lineCounter, 0)
        lineCounter+=1
        #----------------------------------------------------------------------------------------

        label = QLabel('API token:')
        label.setStyleSheet(label_stylesheet)

        self.api_editor = QLineEdit('api token' if not 'api_token' in cur_params
                                    else self.settings_dispatcher.get_value('api_token'))
        self.api_editor.setStyleSheet(line_editor_stylesheet)
        self.api_editor.textChanged.connect(self.api_token_changed)

        self.grid.addWidget(label, lineCounter, 0)
        self.grid.addWidget(self.api_editor, lineCounter, 1)
        lineCounter+=1
        #----------------------------------------------------------------------------------------

        label = QLabel('MT5 account:')
        label.setStyleSheet(label_stylesheet)
        self.host_editor = QLineEdit('host' if not 'mt_host' in cur_params
                                     else self.settings_dispatcher.get_value('mt_host'))
        self.port_editor = QLineEdit('port' if not 'mt_port' in cur_params
                                     else str(self.settings_dispatcher.get_value('mt_port')))

        self.host_editor.setStyleSheet(line_editor_stylesheet)
        self.port_editor.setStyleSheet(line_editor_stylesheet)

        self.host_editor.textChanged.connect(self.host_changed)
        self.port_editor.textChanged.connect(self.port_changed)

        self.grid.addWidget(label, lineCounter, 0)
        self.grid.addWidget(self.host_editor, lineCounter, 1)
        self.grid.addWidget(self.port_editor, lineCounter, 2)
        lineCounter+=1
        #----------------------------------------------------------------------------------------

        label = QLabel("Hedging time (min):")
        label.setStyleSheet(label_stylesheet)
        self.grid.addWidget(label, lineCounter, 0)

        self.hedge_time_editor = QLineEdit("120" if not 'hedge_time' in cur_params else
                                           str(self.settings_dispatcher.get_value('hedge_time')))
        self.hedge_time_editor.setStyleSheet(line_editor_stylesheet)
        self.hedge_time_editor.textChanged.connect(self.hedge_time_editor_changed)
        self.grid.addWidget(self.hedge_time_editor, lineCounter, 1)

        lineCounter+=1
        #----------------------------------------------------------------------------------------

        label = QLabel("Hedging amount:")
        label.setStyleSheet(label_stylesheet)
        self.grid.addWidget(label, lineCounter, 0)

        self.hedge_amount_editor = QLineEdit("1" if not 'hedge_amount' in cur_params else
                                           str(self.settings_dispatcher.get_value('hedge_amount')))
        self.hedge_amount_editor.setStyleSheet(line_editor_stylesheet)
        self.hedge_amount_editor.textChanged.connect(self.hedge_amount_editor_changed)
        self.grid.addWidget(self.hedge_amount_editor, lineCounter, 1)

        lineCounter+=1
        #----------------------------------------------------------------------------------------

        self.save_button = QPushButton('Save')
        self.save_button.setStyleSheet(button_stylesheet)
        self.save_button.clicked.connect(self.save_button_clicked)

        self.grid.addWidget(self.save_button, lineCounter+5, 1)
        #----------------------------------------------------------------------------------------

        self.setLayout(self.grid)


    def api_token_changed(self, api_token):

        self.settings_dispatcher.set_value('api_token', api_token)

    def host_changed(self, host):
        self.settings_dispatcher.set_value('mt_host', host)

    def port_changed(self, port):
        try:
            port = int(port)
            self.settings_dispatcher.set_value('mt_port', port)
        except:
            self.port_editor.clear()

    def hedge_time_editor_changed(self):
        try:
            ht = int(self.hedge_time_editor.text())
            self.settings_dispatcher.set_value('hedge_time', ht)
        except:
            self.hedge_time_editor.close()

    def hedge_amount_editor_changed(self):
        try:
            ha = float(self.hedge_time_editor.text())
            self.settings_dispatcher.set_value('hedge_amount', ha)
        except:
            self.hedge_time_editor.close()

    def save_button_clicked(self):

        self.settings_dispatcher.save()

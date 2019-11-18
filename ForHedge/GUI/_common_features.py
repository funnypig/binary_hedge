
'''
    There are design features which can be used from any window in this module.
'''


def init_styles(self):

    self.head_label_stylesheet = \
    '''
        color : white;
        font-size : 24px;
        font-family : Roboto;
        margin-top: 3px;
        margin-bottom: 3px;
        margin-right: 3px;
        margin-left: 3px;
    '''

    self.label_style_sheet = \
    '''
        color : white;
        font-size : 18px;
        font-family : Roboto;
        font-style : oblique;
        
        margin-top: 3px;
        margin-bottom: 3px;
        margin-right: 3px;
        margin-left: 10px;
    '''

    self.combobox_stylesheet = \
    '''
        color : white;
        font-size : 18px;
        font-family : Roboto;
        font-style : oblique;
        background : #353d52;
        
        margin-top: 3px;
        margin-bottom: 3px;
        margin-right: 3px;
        margin-left: 10px;
    '''

    self.line_edit_stylesheet = \
    '''
        color : #dadada;
        font-size : 18px;
        font-family : Roboto;
        border: 1px solid #adada8;
        
        margin-top: 3px;
        margin-bottom: 3px;
        margin-right: 3px;
        margin-left: 3px;
    '''

    self.button_stylesheet = \
    '''
    QPushButton{
        color : white;
        font-size : 24px;
        font-family : Roboto;
        font-style : bold;
        border-style : solid;
        border-color : #dadada;
        border-width : 1px;
        border-radius : 2px;
    }
    QPushButton:hover{
        background : #557699;
    }
    QPushButton:pressed{
        background : grey;
        font-size : 30px;
    }
    '''

    self.table_stylesheet = \
    '''
    
    QTableView::item:focus{
        background-color: #112833;
    }
    QTableView{
        gridline-color: #007473;
    }
    '''

    self.checkbox_stylesheet = \
    '''
    QCheckBox::indicator {
        border: 1px solid #e7e7e7;
    }
    QCheckBox::indicator:checked {
        background-color : #00bc86;
    }
    QCheckBox::indicator:unchecked {
        background-color : #d13f60;
    }
    '''

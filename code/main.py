import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QDialog, QSizePolicy, QFileDialog
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QDateEdit, QCheckBox, QPushButton, QComboBox, QHeaderView
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import Qt, QSize, QDate
import sqlite3
import pandas as pd
import numpy as np

# Common Functions
def ShowWarning(self, msg):
    QMessageBox.warning(self, '전자정부 수출실적 DB', msg, QMessageBox.Close, QMessageBox.Close)

def GetColItem(value, isRight=False, isReadOnly=False):
    text = ''
    if type(value) != type(text):
        text = str(value)
    else:
        text = value
    item = QTableWidgetItem(text)
    if isRight == True:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
    else:
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignCenter)
    if isReadOnly == True:
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
    return item


class ProjectData:
    def __init__(self):
        self.df_project = None
        self.df_project_country = None
        self.df_project_contractor = None
        self.df_project_fund = None
        self.df_country = None
        self.df_region = None
        self.df_fundtype = None
        self.df_contractor = None
        self.df_contractortype = None
        self.df_contact = None
        self.df_tasktype = None
        self.df_project_tasktype = None

    def load_db(self, db_path):
        con = sqlite3.connect(db_path)
        self.df_project = pd.read_sql("SELECT * FROM project", con)
        self.df_project.fillna(0, inplace=True)
        self.df_project = self.df_project.astype({'id': np.int, 'year': np.int, 'price': np.int})
        self.df_project_country = pd.read_sql("SELECT * FROM project_country", con)
        self.df_project_contractor = pd.read_sql("SELECT * FROM project_contractor", con)
        self.df_project_fund = pd.read_sql("SELECT * FROM project_fund", con)
        self.df_project_fund.fillna(0, inplace=True)
        self.df_project_fund = self.df_project_fund.astype({'amount': np.int})
        self.df_country = pd.read_sql("SELECT * FROM country", con)
        self.df_region = pd.read_sql("SELECT * FROM region", con)
        self.df_fundtype = pd.read_sql("SELECT * FROM fundtype", con)
        self.df_contractor = pd.read_sql("SELECT * FROM contractor", con)
        self.df_contractortype = pd.read_sql("SELECT * FROM contractortype", con)
        self.df_contact = pd.read_sql("SELECT * FROM contact", con)
        self.df_tasktype = pd.read_sql("SELECT * FROM tasktype", con)
        self.df_project_tasktype = pd.read_sql("SELECT * FROM project_tasktype", con)
        con.close()

    def copy(self):
        replica = ProjectData()
        replica.df_project = self.df_project.copy()
        replica.df_project_country = self.df_project_country.copy()
        replica.df_project_contractor = self.df_project_contractor.copy()
        replica.df_project_fund = self.df_project_fund.copy()
        replica.df_country = self.df_country.copy()
        replica.df_region = self.df_region.copy()
        replica.df_fundtype = self.df_fundtype.copy()
        replica.df_contractor = self.df_contractor.copy()
        replica.df_contractortype = self.df_contractortype.copy()
        replica.df_contact = self.df_contact.copy()
        replica.df_tasktype = self.df_tasktype.copy()
        replica.df_project_tasktype = self.df_project_tasktype.copy()
        return replica


class QMyListWidgetItem (QListWidgetItem):
    def __init__(self):
        super().__init__()
        self.item_data = None

    def setItemData(self, data):
        self.item_data = data

    def getItemData(self):
        return self.item_data

class QMyComboBox (QComboBox):
    def __init__(self):
        super().__init__()

    def wheelEvent(self, e):
        e.ignore()


class MyMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.projectData = ProjectData()
        self.db_path = 'egovexport.db'
        self.init_ui()

    def init_ui(self):
        self.projectTableWidget = ProjectTableWidget(self)
        loadAction = QAction(QIcon('load.png'), '불러오기', self)
        loadAction.setShortcut('Ctrl+l')
        loadAction.setStatusTip('불러오기')
        loadAction.triggered.connect(self.event_load_db)

        saveAction = QAction(QIcon('save.png'), '저장하기', self)
        saveAction.setShortcut('Ctrl+s')
        saveAction.setStatusTip('저장하기')
        saveAction.triggered.connect(self.event_save_db)

        exitAction = QAction(QIcon('exit.png'), '종료', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('종료')
        exitAction.triggered.connect(qApp.quit)
        
        addItemAction = QAction(QIcon('add.png'), '추가', self)
        addItemAction.setShortcut('Ctrl+a')
        addItemAction.setStatusTip('항목 추가')
        addItemAction.triggered.connect(self.projectTableWidget.add_project)
        
        editItemAction = QAction(QIcon('edit.png'), '수정', self)
        editItemAction.setShortcut('Ctrl+e')
        editItemAction.setStatusTip('항목 수정')
        editItemAction.triggered.connect(self.projectTableWidget.event_edit)
        
        delItemAction = QAction(QIcon('delete.png'), '삭제', self)
        delItemAction.setShortcut('Ctrl+d')
        delItemAction.setStatusTip('항목 삭제')
        delItemAction.triggered.connect(self.projectTableWidget.event_delete)

        refreshAction = QAction(QIcon('refresh.png'), '새로고침', self)
        refreshAction.setShortcut('Ctrl+r')
        refreshAction.setStatusTip('새로고침')
        refreshAction.triggered.connect(self.refresh_data)

        viewContractorAction = QAction(QIcon('db.png'), '사업자 보기', self)
        viewContractorAction.setShortcut('Ctrl+1')
        viewContractorAction.setStatusTip('사업자 보기')
        viewContractorAction.triggered.connect(self.event_view_contractor)

        viewContactAction = QAction(QIcon('db.png'), '연락처 보기', self)
        viewContactAction.setShortcut('Ctrl+2')
        viewContactAction.setStatusTip('연락처 보기')
        viewContactAction.triggered.connect(self.event_view_contact)

        viewFundTypeAction = QAction(QIcon('db.png'), '자금유형 보기', self)
        viewFundTypeAction.setShortcut('Ctrl+3')
        viewFundTypeAction.setStatusTip('자금유형 보기')
        viewFundTypeAction.triggered.connect(self.event_view_fundtype)

        viewTaskTypeAction = QAction(QIcon('db.png'), '과업유형 보기', self)
        viewTaskTypeAction.setShortcut('Ctrl+4')
        viewTaskTypeAction.setStatusTip('과업유형 보기')
        viewTaskTypeAction.triggered.connect(self.event_view_tasktype)

        viewCountryAction = QAction(QIcon('db.png'), '국가 보기', self)
        viewCountryAction.setShortcut('Ctrl+5')
        viewCountryAction.setStatusTip('국가 보기')
        viewCountryAction.triggered.connect(self.event_view_country)

        viewRegionAction = QAction(QIcon('db.png'), '지역 보기', self)
        viewRegionAction.setShortcut('Ctrl+6')
        viewRegionAction.setStatusTip('지역 보기')
        viewRegionAction.triggered.connect(self.event_view_region)

        viewContractorTypeAction = QAction(QIcon('db.png'), '기업분류 보기', self)
        viewContractorTypeAction.setShortcut('Ctrl+7')
        viewContractorTypeAction.setStatusTip('기업분류 보기')
        viewContractorTypeAction.triggered.connect(self.event_view_contractortype)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        menuDB = menubar.addMenu('&데이터베이스')
        menuDB.addAction(loadAction)
        menuDB.addAction(saveAction)
        menuDB.addSeparator()
        menuDB.addAction(exitAction)
        menuProject = menubar.addMenu('&사업 정보')
        menuProject.addAction(addItemAction)
        menuProject.addAction(editItemAction)
        menuProject.addAction(delItemAction)
        menuProject.addSeparator()
        menuProject.addAction(refreshAction)
        menuContractor = menubar.addMenu('&사업자 정보')
        menuContractor.addAction(viewContractorAction)
        menuContractor.addAction(viewContactAction)
        menuEtc = menubar.addMenu('&기타정보')
        menuEtc.addAction(viewFundTypeAction)
        menuEtc.addAction(viewTaskTypeAction)
        menuEtc.addAction(viewCountryAction)
        menuEtc.addAction(viewRegionAction)
        menuEtc.addAction(viewContractorTypeAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(loadAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(addItemAction)
        self.toolbar.addAction(editItemAction)
        self.toolbar.addAction(delItemAction)
        self.toolbar.addAction(refreshAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(exitAction)
        self.toolbar.setIconSize(QSize(32, 48))
        self.toolbar.setStyleSheet("QToolBar{spacing:16px;}")

        self.setCentralWidget(self.projectTableWidget)
        self.setWindowTitle('전자정부 수출실적 데이터베이스')
        self.setWindowIcon(QIcon('db.png'))
        self.setGeometry(300, 300, 700, 450)
        self.load_db(self.db_path)
        self.show()

    def check_db(self, db_path):
        try:
            con = sqlite3.connect(db_path)
            cursor = con.cursor()
            cursor.execute("select * from project")
            con.close()
        except Exception as err:
            ShowWarning(self, str(err))
            return False
        return True

    def event_load_db(self):
        fname = QFileDialog.getOpenFileName(self, '데이터베이스 파일을 선택해 주세요', './', "SQLite Database (*.db)")
        db_path = fname[0]
        if db_path:
            if self.check_db(db_path):
                self.load_db(db_path)
            else:
                ShowWarning(self, "적합한 데이터베이스 파일이 아닙니다.")

    def event_save_db(self):
        reply = QMessageBox.question(self, '데이터베이스 저장', '변경사항을 데이터베이스에 저장하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_db()

    def load_db(self, db_path):
        self.statusBar().showMessage('DB에서 데이터를 읽어들이고 있습니다...')
        self.projectData.load_db(db_path)
        self.projectTableWidget.loadData()
        self.statusBar().showMessage('DB 데이터 읽기가 완료되었습니다.')
        self.setWindowTitle('전자정부 수출실적 데이터베이스: ' + db_path)
        self.db_path = db_path

    def save_db(self):
        data = self.projectData
        try:
            con = sqlite3.connect(self.db_path)
            data.df_project.to_sql('project', con, if_exists='replace', index=False)
            data.df_project_country.to_sql('project_country', con, if_exists='replace', index=False)
            data.df_project_contractor.to_sql('project_contractor', con, if_exists='replace', index=False)
            data.df_project_fund.to_sql('project_fund', con, if_exists='replace', index=False)
            data.df_project_tasktype.to_sql('project_tasktype', con, if_exists='replace', index=False)
            data.df_contractor.to_sql('contractor', con, if_exists='replace', index=False)
            data.df_contact.to_sql('contact', con, if_exists='replace', index=False)
            #data.df_fundtype.to_sql('fundtype', con, if_exists='replace', index=False)
            #data.df_country.to_sql('country', con, if_exists='replace', index=False)
            #data.df_region.to_sql('region', con, if_exists='replace', index=False)
            #data.df_contractortype.to_sql('contractortype', con, if_exists='replace', index=False)
            #data.df_tasktype.to_sql('tasktype', con, if_exists='replace', index=False)
            con.close()
        except Exception as err:
            ShowWarning(self, str(err))
            return False
        ShowWarning(self, "데이터베이스에 저장되었습니다..")
        return True

    def refresh_data(self):
        self.load_db(self.db_path)

    def event_view_contractor(self):
        dlg = ModalEditorDialog(self, 'contractor')
        dlg.exec_()
        if dlg.is_changed() == True:
            self.projectTableWidget.loadData()

    def event_view_contact(self):
        dlg = ModalEditorDialog(self, 'contact')
        dlg.exec_()

    def event_view_country(self):
        dlg = ModalEditorDialog(self, 'country')
        dlg.exec_()

    def event_view_fundtype(self):
        dlg = ModalEditorDialog(self, 'fundtype')
        dlg.exec_()

    def event_view_tasktype(self):
        dlg = ModalEditorDialog(self, 'tasktype')
        dlg.exec_()

    def event_view_region(self):
        dlg = ModalEditorDialog(self, 'region')
        dlg.exec_()

    def event_view_contractortype(self):
        dlg = ModalEditorDialog(self, 'contractortype')
        dlg.exec_()


class ProjectTableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__()
        self.projectData = parent.projectData
        self.init_ui()

    def init_ui(self):
        self.setRowCount(0)
        self.setColumnCount(12)
        self.horizontalHeader().setStyleSheet("::section{Background-color:rgb(190,200,220);}")
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStyleSheet("::section{Background-color:rgb(195,220,235);}")
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        column_headers = ['코드', '사업명', '귀속년도', '금액', '수요국가', '자금출처', '사업자', '착수일', '종료일', '과업유형', '영문사업명', '비고']
        column_widths = [40, 200, 60, 100, 100, 100, 100, 80, 80, 100, 150, 100]
        self.setHorizontalHeaderLabels(column_headers)
        for index in range(0, len(column_widths)):
            self.setColumnWidth(index, column_widths[index])
        #Events
        self.cellDoubleClicked.connect(self.event_cellDoubleClicked)

    def event_edit(self):
        if self.currentItem():
            self.edit_project(self.currentItem().row())

    def event_delete(self):
        while self.selectedItems():
            index = self.selectedItems()[0].row()
            self.delete_project(index)

    def event_cellDoubleClicked(self, row, col):
        self.edit_project(row)

    def loadData(self):
        data = self.projectData
        self.clearContents()
        self.setRowCount(0)
        for index, row in data.df_project.iterrows():
            new_row_index = self.rowCount()
            self.insertRow(new_row_index)
            self.updateRow(new_row_index, row)
        self.resizeRowsToContents()

    def updateRow(self, row_index, row):
        data = self.projectData
        self.setItem(row_index, 0, GetColItem(row['id'], True))
        self.setItem(row_index, 1, GetColItem(row['name']))
        self.setItem(row_index, 2, GetColItem(row['year']))
        self.setItem(row_index, 3, GetColItem('${:,}'.format(row['price']), True))
        self.setItem(row_index, 4, self.GetCountry(row['id'], data))
        self.setItem(row_index, 5, self.GetFundType(row['id'], data))
        self.setItem(row_index, 6, self.GetContractor(row['id'], data))
        self.setItem(row_index, 7, GetColItem(row['startdate']))
        self.setItem(row_index, 8, GetColItem(row['enddate']))
        self.setItem(row_index, 9, self.GetTaskType(row['id'], data))
        self.setItem(row_index, 10, GetColItem(row['nameeng']))
        self.setItem(row_index, 11, GetColItem(row['memo']))

    def GetNames(self, df):
        names = ''
        for index, row in df.iterrows():
            names += row['name'] + '/'
        if names != '':
            names = names[:-1]
        return GetColItem(names)

    def GetCountry(self, project_id, data):
        df_merged = pd.merge(data.df_project_country, data.df_country, left_on='country_id', right_on='id')[['project_id', 'name']]
        df_selected = df_merged.query('project_id == {}'.format(project_id))
        return self.GetNames(df_selected)

    def GetContractor(self, project_id, data):
        df_merged = pd.merge(data.df_project_contractor, data.df_contractor, left_on='contractor_id', right_on='id')[['project_id', 'name']]
        df_selected = df_merged.query('project_id == {}'.format(project_id))
        return self.GetNames(df_selected)

    def GetFundType(self, project_id, data):
        df_merged = pd.merge(data.df_project_fund, data.df_fundtype, left_on='fundtype_id', right_on='id')[['project_id', 'name']]
        df_selected = df_merged.query('project_id == {}'.format(project_id))
        return self.GetNames(df_selected)

    def GetTaskType(self, project_id, data):
        df_merged = pd.merge(data.df_project_tasktype, data.df_tasktype, left_on='tasktype_id', right_on='id')[['project_id', 'name']]
        df_selected = df_merged.query('project_id == {}'.format(project_id))
        return self.GetNames(df_selected)

    def add_project(self):
        dlg = ProjectFormDialog(self, None)
        if dlg.exec_() == QDialog.Accepted:
            self.projectData.df_project = dlg.projectData.df_project
            self.projectData.df_project_country = dlg.projectData.df_project_country
            self.projectData.df_project_contractor = dlg.projectData.df_project_contractor
            self.projectData.df_project_fund = dlg.projectData.df_project_fund
            self.projectData.df_project_tasktype = dlg.projectData.df_project_tasktype
            row = self.projectData.df_project[self.projectData.df_project['id'] == dlg.project_id].iloc[0]
            new_row_index = self.rowCount()
            self.insertRow(new_row_index)
            self.updateRow(new_row_index, row)

    def edit_project(self, row_index):
        project_id = int(self.item(row_index, 0).text())  # Retrieve ID
        dlg = ProjectFormDialog(self, project_id)
        if dlg.exec_() == QDialog.Accepted:
            self.projectData.df_project = dlg.projectData.df_project
            self.projectData.df_project_country = dlg.projectData.df_project_country
            self.projectData.df_project_contractor = dlg.projectData.df_project_contractor
            self.projectData.df_project_fund = dlg.projectData.df_project_fund
            self.projectData.df_project_tasktype = dlg.projectData.df_project_tasktype
            row = self.projectData.df_project[self.projectData.df_project['id'] == dlg.project_id].iloc[0]
            self.updateRow(row_index, row)

    def delete_project(self, row_index):
        project_id = int(self.item(row_index, 0).text())  # Retrieve ID
        # 국가 목록
        df_temp = self.projectData.df_project_country
        index = df_temp.query('project_id == {}'.format(project_id)).index
        self.projectData.df_project_country = df_temp.drop(index)
        # 사업자 목록
        df_temp = self.projectData.df_project_contractor
        index = df_temp.query('project_id == {}'.format(project_id)).index
        self.projectData.df_project_contractor = df_temp.drop(index)
        # 자금유형 목록
        df_temp = self.projectData.df_project_fund
        index = df_temp.query('project_id == {}'.format(project_id)).index
        self.projectData.df_project_fund = df_temp.drop(index)
        # 과업유형 목록
        df_temp = self.projectData.df_project_tasktype
        index = df_temp.query('project_id == {}'.format(project_id)).index
        self.projectData.df_project_tasktype = df_temp.drop(index)
        # 사업 데이터 본체
        df_temp = self.projectData.df_project
        index = df_temp.query('id == {}'.format(project_id)).index
        self.projectData.df_project = df_temp.drop(index)
        # UI에서 삭제
        self.removeRow(row_index)


class ProjectFormDialog(QDialog):
    def __init__(self, parent, project_id=None):
        super().__init__()
        self.projectData = parent.projectData.copy()
        self.project_id = project_id
        self.add_new = True
        if project_id is not None:
            self.add_new = False
        else:
            if len(self.projectData.df_project['id'].index) == 0:
                self.project_id = 0
            else:
                self.project_id = self.projectData.df_project['id'].max() + 1
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon('add.png'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Initialize UI Objects for Project Attributes
        self.ui_name = QLineEdit()
        self.ui_year = QLineEdit()
        self.ui_year.setValidator(QIntValidator(1967, 9999))
        self.ui_price = QLineEdit()
        self.ui_price.setAlignment(Qt.AlignRight)
        self.ui_price.setValidator(QIntValidator(0, 999999999))
        self.ui_startdate = QDateEdit(calendarPopup=True)
        self.ui_enddate = QDateEdit(calendarPopup=True)
        self.ui_nameeng = QLineEdit()
        self.ui_memo = QLineEdit()
        self.ui_countries = QListWidget()
        self.ui_countries.setFlow(0)
        self.ui_countries.setWrapping(True)
        self.ui_countries.setMinimumHeight(40)
        self.ui_countries_add = QPushButton("추가...")
        self.ui_countries_del = QPushButton("삭제")
        self.ui_countries_add.clicked.connect(self.event_btn_addCountry)
        self.ui_countries_del.clicked.connect(self.event_btn_delCountry)
        self.ui_contractors = QListWidget()
        self.ui_contractors.setFlow(0)
        self.ui_contractors.setWrapping(True)
        self.ui_contractors.setMinimumHeight(40)
        self.ui_contractors_add = QPushButton("추가...")
        self.ui_contractors_del = QPushButton("삭제")
        self.ui_contractors_add.clicked.connect(self.event_btn_addContractor)
        self.ui_contractors_del.clicked.connect(self.event_btn_delContractor)
        self.ui_fundtypes = QListWidget()
        self.ui_fundtypes.setFlow(0)
        self.ui_fundtypes.setWrapping(True)
        self.ui_fundtypes.setMinimumHeight(40)
        self.ui_fundtypes_add = QPushButton("추가...")
        self.ui_fundtypes_del = QPushButton("삭제")
        self.ui_fundtypes_add.clicked.connect(self.event_btn_addFundType)
        self.ui_fundtypes_del.clicked.connect(self.event_btn_delFundType)
        self.ui_tasktypes = QListWidget()
        self.ui_tasktypes.setFlow(0)
        self.ui_tasktypes.setWrapping(True)
        self.ui_tasktypes.setMinimumHeight(40)
        self.ui_tasktypes_add = QPushButton("추가...")
        self.ui_tasktypes_del = QPushButton("삭제")
        self.ui_tasktypes_add.clicked.connect(self.event_btn_addTaskType)
        self.ui_tasktypes_del.clicked.connect(self.event_btn_delTaskType)
        print(3)
        # Initialize UI Objects for Dialog Ok/Cancel Buttons
        self.ui_ok = QPushButton("저장")
        self.ui_ok.setMinimumHeight(30)
        self.ui_ok.clicked.connect(self.event_btn_ok)
        self.ui_cancel = QPushButton("취소")
        self.ui_cancel.setMinimumHeight(30)
        self.ui_cancel.clicked.connect(self.event_btn_cancel)
        # Initialize UI Layout
        self.resize(400, 300)
        grid = QGridLayout()
        self.setLayout(grid)
        gr = 0  # Grid Row
        grid.addWidget(QLabel('사업이름'), gr, 0, 1, 1)
        grid.addWidget(self.ui_name, gr, 1, 1, 6)
        gr += 1
        grid.addWidget(QLabel('귀속년도'), gr, 0, 1, 1)
        grid.addWidget(self.ui_year, gr, 1, 1, 2)
        gr += 1
        grid.addWidget(QLabel('사업규모'), gr, 0, 1, 1)
        grid.addWidget(self.ui_price, gr, 1, 1, 2)
        grid.addWidget(QLabel('USD'), gr, 3, 1, 1)
        gr += 1
        grid.addWidget(QLabel('사업기간'), gr, 0, 1, 1)
        grid.addWidget(self.ui_startdate, gr, 1, 1, 2)
        grid.addWidget(QLabel('부터'), gr, 3, 1, 1)
        grid.addWidget(self.ui_enddate, gr, 4, 1, 2)
        grid.addWidget(QLabel('까지'), gr, 6, 1, 1)
        gr += 1
        grid.addWidget(QLabel('대상국가'), gr, 0, 1, 1)
        grid.addWidget(self.ui_countries, gr, 1, 1, 4)
        grid.addWidget(self.ui_countries_add, gr, 5, 1, 1)
        grid.addWidget(self.ui_countries_del, gr, 6, 1, 1)
        gr += 1
        grid.addWidget(QLabel('사업자'), gr, 0, 1, 1)
        grid.addWidget(self.ui_contractors, gr, 1, 1, 4)
        grid.addWidget(self.ui_contractors_add, gr, 5, 1, 1)
        grid.addWidget(self.ui_contractors_del, gr, 6, 1, 1)
        gr += 1
        grid.addWidget(QLabel('자금유형'), gr, 0, 1, 1)
        grid.addWidget(self.ui_fundtypes, gr, 1, 1, 4)
        grid.addWidget(self.ui_fundtypes_add, gr, 5, 1, 1)
        grid.addWidget(self.ui_fundtypes_del, gr, 6, 1, 1)
        gr += 1
        grid.addWidget(QLabel('과업유형'), gr, 0, 1, 1)
        grid.addWidget(self.ui_tasktypes, gr, 1, 1, 4)
        grid.addWidget(self.ui_tasktypes_add, gr, 5, 1, 1)
        grid.addWidget(self.ui_tasktypes_del, gr, 6, 1, 1)
        gr += 1
        grid.addWidget(QLabel('영문명칭'), gr, 0, 1, 1)
        grid.addWidget(self.ui_nameeng, gr, 1, 1, 6)
        gr += 1
        grid.addWidget(QLabel('비고'), gr, 0, 1, 1)
        grid.addWidget(self.ui_memo, gr, 1, 1, 6)
        gr += 1
        grid.addWidget(self.ui_ok, gr, 5, 1, 1)
        grid.addWidget(self.ui_cancel, gr, 6, 1, 1)
        if self.add_new:
            self.setWindowTitle("사업 추가 등록")
        else:
            self.setWindowTitle("사업 정보 수정(사업번호: {})".format(str(self.project_id)))
            self.loadProject()
        self.ui_ok.setDefault(True)
        self.ui_name.setFocus()

    def event_btn_ok(self):
        if not self.updateProject():
            return
        self.accept()

    def event_btn_cancel(self):
        self.reject()

    def addItem(self, item_type):
        dlg = AddListItemDialog(self, item_type)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            item_id = int(dlg.selected_item)
            if item_type == 'country':
                df_temp = self.projectData.df_project_country
            elif item_type == 'contractor':
                df_temp = self.projectData.df_project_contractor
            elif item_type == 'fundtype':
                df_temp = self.projectData.df_project_fund
            elif item_type == 'tasktype':
                df_temp = self.projectData.df_project_tasktype
            else:
                return
            if df_temp.query('{}_id == {} and project_id == {}'.format(item_type, item_id, self.project_id)).empty: # 중복 거르기
                if dlg.number is not None and np.isnan(dlg.number) == False and item_type == 'fundtype':
                    df_temp = df_temp.append({'project_id': self.project_id, '{}_id'.format(item_type): item_id, 'amount': dlg.number}, ignore_index=True)
                else:
                    df_temp = df_temp.append({'project_id': self.project_id, '{}_id'.format(item_type): item_id}, ignore_index=True)
                # Pandas에서 NaN 값이 들어가면 모든 int가 float로 바뀌는 문제 해결용,
                df_temp = df_temp.astype({'project_id': np.int, '{}_id'.format(item_type): np.int})
                if item_type == 'country':
                    self.projectData.df_project_country = df_temp
                elif item_type == 'contractor':
                    self.projectData.df_project_contractor = df_temp
                elif item_type == 'fundtype':
                    self.projectData.df_project_fund = df_temp
                elif item_type == 'tasktype':
                    self.projectData.df_project_tasktype = df_temp
                self.loadItemList(item_type)

    def delItem(self, item_type):
        if item_type == 'country':
            ui = self.ui_countries
            df_temp = self.projectData.df_project_country
        elif item_type == 'contractor':
            ui = self.ui_contractors
            df_temp = self.projectData.df_project_contractor
        elif item_type == 'fundtype':
            ui = self.ui_fundtypes
            df_temp = self.projectData.df_project_fund
        elif item_type == 'tasktype':
            ui = self.ui_tasktypes
            df_temp = self.projectData.df_project_tasktype
        else:
            return
        items = ui.selectedItems()
        for item in items:
            index = df_temp.query('{}_id == {} and project_id == {}'.format(item_type, item.getItemData(), self.project_id)).index
            if item_type == 'country':
                self.projectData.df_project_country = df_temp.drop(index)
            elif item_type == 'contractor':
                self.projectData.df_project_contractor = df_temp.drop(index)
            elif item_type == 'fundtype':
                self.projectData.df_project_fund = df_temp.drop(index)
            elif item_type == 'tasktype':
                self.projectData.df_project_tasktype = df_temp.drop(index)
        self.loadItemList(item_type)

    def event_btn_addCountry(self):
        self.addItem('country')
    def event_btn_delCountry(self):
        self.delItem('country')
    def event_btn_addContractor(self):
        self.addItem('contractor')
    def event_btn_delContractor(self):
        self.delItem('contractor')
    def event_btn_addFundType(self):
        self.addItem('fundtype')
    def event_btn_delFundType(self):
        self.delItem('fundtype')
    def event_btn_addTaskType(self):
        self.addItem('tasktype')
    def event_btn_delTaskType(self):
        self.delItem('tasktype')

    def loadItemList(self, item_type):
        data = self.projectData
        project_id = self.project_id
        item_id_col = item_type + '_id'
        if item_type == 'country':
            ui = self.ui_countries
            df_temp1 = data.df_project_country
            df_temp2 = data.df_country
            col_retrieve = ['project_id', item_id_col, 'name']
        elif item_type == 'contractor':
            ui = self.ui_contractors
            df_temp1 = data.df_project_contractor
            df_temp2 = data.df_contractor
            col_retrieve = ['project_id', item_id_col, 'name']
        elif item_type == 'fundtype':
            ui = self.ui_fundtypes
            df_temp1 = data.df_project_fund
            df_temp2 = data.df_fundtype
            col_retrieve = ['project_id', item_id_col, 'name', 'amount']
        elif item_type == 'tasktype':
            ui = self.ui_tasktypes
            df_temp1 = data.df_project_tasktype
            df_temp2 = data.df_tasktype
            col_retrieve = ['project_id', item_id_col, 'name']
        else:
            return
        ui.clear()
        df_merged = pd.merge(df_temp1, df_temp2, left_on=item_id_col, right_on='id')[col_retrieve]
        df_selected = df_merged.query('project_id == {}'.format(project_id))
        for index, row in df_selected.iterrows():
            item = QMyListWidgetItem()
            item.setItemData(row[item_id_col])
            if item_type == 'fundtype':
                text = '{}'.format(row['name'])
                if row['amount'] > 0:
                    text += '(${})'.format(int(row['amount']))
                item.setText(text)
            else:
                item.setText(row['name'])
            ui.addItem(item)

    def loadProject(self):
        data = self.projectData
        project_id = self.project_id
        project = data.df_project[data.df_project['id'] == project_id].iloc[0]
        if project['name']:
            self.ui_name.setText(project['name'])
        if project['year']:
            self.ui_year.setText(str(project['year']))
        if project['price']:
            self.ui_price.setText(str(project['price']))
        if project['startdate']:
            self.ui_startdate.setDate(QDate.fromString(project['startdate'], Qt.ISODate))
        if project['enddate']:
            self.ui_enddate.setDate(QDate.fromString(project['enddate'], Qt.ISODate))
        self.loadItemList('country')
        self.loadItemList('contractor')
        self.loadItemList('fundtype')
        self.loadItemList('tasktype')
        if project['nameeng']:
            self.ui_nameeng.setText(str(project['nameeng']))
        if project['memo']:
            self.ui_memo.setText(str(project['memo']))

    def updateProject(self):
        project_id = self.project_id
        name = self.ui_name.text()
        if not name:
            ShowWarning(self, '사업명을 입력해 주세요.')
            return False
        year_text = self.ui_year.text()
        year = 0
        if year_text:
            year = int(year_text)
        if year == 0:
            ShowWarning(self, '귀속년도를 입력해 주세요.')
            return False
        price_text = self.ui_price.text()
        price = 0
        if price_text:
            price = int(price_text)
        if price == 0:
            ShowWarning(self, '사업규모를 입력해 주세요.')
            return False
        startdate = self.ui_startdate.date().toString(Qt.ISODate)
        enddate = self.ui_enddate.date().toString(Qt.ISODate)
        nameeng = self.ui_nameeng.text()
        memo = self.ui_memo.text()
        df_update = pd.DataFrame(
            {'id': [project_id], 'name': [name], 'year': [year], 'price': [price],
             'startdate': [startdate], 'enddate': [enddate], 'nameeng': [nameeng], 'memo': [memo]})
        if self.add_new:  # 추가
            self.projectData.df_project = self.projectData.df_project.append(df_update, ignore_index=True)
        else:  # 수정
            self.projectData.df_project.set_index('id', inplace=True)
            self.projectData.df_project.update(df_update.set_index('id'))
            self.projectData.df_project.reset_index(inplace=True)
        self.projectData.df_project = self.projectData.df_project.astype({'id': np.int, 'year': np.int, 'price': np.int})
        return True


class AddListItemDialog(QDialog):
    def __init__(self, parent, item_type='country'):
        super().__init__()
        self.projectData = parent.projectData
        self.itemType = item_type
        self.selected_item = None
        self.number = None
        self.init_ui()

    def init_ui(self):
        self.ui_combo_label = QLabel()
        self.ui_combo = QComboBox()
        self.ui_combo.setEditable(True)
        self.ui_combo.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.ui_combo.setInsertPolicy(QComboBox.NoInsert)
        self.ui_number_label = QLabel()
        self.ui_number = QLineEdit()
        self.ui_number.setValidator(QIntValidator(0, 999999999))
        self.ui_number.setAlignment(Qt.AlignRight)
        self.ui_ok = QPushButton('추가')
        self.ui_ok.setMinimumHeight(30)
        self.ui_ok.clicked.connect(self.event_btn_ok)
        self.ui_cancel = QPushButton('취소')
        self.ui_cancel.setMinimumHeight(30)
        self.ui_cancel.clicked.connect(self.event_btn_cancel)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        grid = QGridLayout()
        self.setLayout(grid)
        self.resize(200, 50)
        grid.addWidget(self.ui_combo_label, 0, 0, 1, 2)
        grid.addWidget(self.ui_combo, 1, 0, 1, 2)
        grid.addWidget(self.ui_ok, 4, 0, 1, 1)
        grid.addWidget(self.ui_cancel, 4, 1, 1, 1)

        if self.itemType == 'country':
            self.setWindowTitle("국가 추가")
            self.ui_combo_label.setText("국가")
            self.loadItems(self.projectData.df_country)
        elif self.itemType == 'contractor':
            self.setWindowTitle("사업자 추가")
            self.ui_combo_label.setText("사업자")
            self.loadItems(self.projectData.df_contractor)
        elif self.itemType == 'fundtype':
            self.setWindowTitle("자금유형 추가")
            grid.addWidget(self.ui_number_label, 2, 0, 1, 2)
            grid.addWidget(self.ui_number, 3, 0, 1, 2)
            self.ui_combo_label.setText("자금유형")
            self.ui_number_label.setText("금액(USD)")
            self.loadItems(self.projectData.df_fundtype, False)
        elif self.itemType == 'tasktype':
            self.setWindowTitle("과업유형 추가")
            self.ui_combo_label.setText("과업유형")
            self.loadItems(self.projectData.df_tasktype)

    def loadItems(self, data, sort_by_name=True):
        if sort_by_name:
            data = data.sort_values(by=['name'])
        for index, row in data.iterrows():
            newIndex = self.ui_combo.count()
            self.ui_combo.addItem(row['name'])
            self.ui_combo.setItemData(newIndex, row['id'])

    def event_btn_ok(self):
        if self.ui_combo.findText(self.ui_combo.currentText()) == -1:
            ShowWarning(self, '입력된 내용과 일치하는 항목이 없습니다.')
            return
        self.selected_item = self.ui_combo.itemData(self.ui_combo.currentIndex())
        if self.ui_number.text():
            self.number = int(self.ui_number.text())
        self.accept()

    def event_btn_cancel(self):
        self.selected_item = None
        self.reject()

class ModalEditorTableWidget(QTableWidget):
    def __init__(self, parent, table_type):
        super().__init__()
        self.projectData = parent.projectData
        self.tempData = parent.projectData.copy()
        self.changed = False
        self.table_type = table_type
        self.init_ui()

    def init_ui(self):
        if self.table_type == 'contractor':
            column_headers = ['', '코드', '사업자명', '사업자 유형', '사업자 등록번호', '법인번호', '참조회수']
            column_widths = [15, 40, 100, 100, 100, 100, 60]
        elif self.table_type == 'contact':
            column_headers = ['', '코드', '이름', '소속', '전화번호', '이메일', '주소', '갱신일자']
            column_widths = [15, 40, 100, 100, 100, 100, 100, 100]
        elif self.table_type == 'fundtype':
            column_headers = ['', '코드', '자금유형', '참조회수']
            column_widths = [15, 40, 100, 60]
        elif self.table_type == 'country':
            column_headers = ['', '코드', '국가명', '지역', '참조회수']
            column_widths = [15, 40, 100, 150, 60]
        elif self.table_type == 'region':
            column_headers = ['', '코드', '지역', '참조회수']
            column_widths = [15, 40, 150, 60]
        elif self.table_type == 'contractortype':
            column_headers = ['', '코드', '분류', '참조회수']
            column_widths = [15, 40, 100, 60]
        elif self.table_type == 'tasktype':
            column_headers = ['', '코드', '유형', '참조회수']
            column_widths = [15, 40, 100, 60]

        self.setRowCount(0)
        self.setColumnCount(len(column_headers))
        self.setHorizontalHeaderLabels(column_headers)
        h_header = self.horizontalHeader();
        h_header.setStyleSheet("::section{Background-color:rgb(190,200,220);}")
        self.verticalHeader().setStyleSheet("::section{Background-color:rgb(195,220,235);}")
        h_header.setSectionResizeMode(0, QHeaderView.Fixed)
        for index in range(0, len(column_widths)):
            self.setColumnWidth(index, column_widths[index])
        """self.cellActivated.connect(self.handleCellActivated)
        self.cellClicked.connect(self.handleCellClicked)
        self.cellDoubleClicked.connect(self.handleCellDoubleClicked)
        self.cellEntered.connect(self.handleCellEntered)
        self.cellPressed.connect(self.handleCellPressed)
        self.cellChanged.connect(self.handleCellChanged)"""
        self.loadData()

    """def handleCellActivated(self, row, column):
        print("cellActivated", row, column)
    def handleCellClicked(self, row, column):
        print("cellClicked", row, column)
    def handleCellDoubleClicked(self, row, column):
        print("cellDoubleClicked", row, column)
    def handleCellEntered(self, row, column):
        print("cellEntered", row, column)
    def handleCellPressed(self, row, column):
        print("cellPressed", row, column)
    def handleCellChanged(self, row, column):
        print("cellChanged", row, column)"""

    def get_df(self):
        if self.table_type == 'contractor':
            return self.tempData.df_contractor
        elif self.table_type == 'contact':
            return self.tempData.df_contact
        elif self.table_type == 'fundtype':
            return self.tempData.df_fundtype
        elif self.table_type == 'country':
            return self.tempData.df_country
        elif self.table_type == 'region':
            return self.tempData.df_region
        elif self.table_type == 'contractortype':
            return self.tempData.df_contractortype
        elif self.table_type == 'tasktype':
            return self.tempData.df_tasktype
        else:
            return None

    def set_df(self, df_temp):
        if self.table_type == 'contractor':
            self.tempData.df_contractor = df_temp
        elif self.table_type == 'contact':
            self.tempData.df_contact = df_temp
        elif self.table_type == 'fundtype':
            self.tempData.df_fundtype = df_temp
        elif self.table_type == 'country':
            self.tempData.df_country = df_temp
        elif self.table_type == 'region':
            self.tempData.df_region = df_temp
        elif self.table_type == 'contractortype':
            self.tempData.df_contractortype = df_temp
        elif self.table_type == 'tasktype':
            self.tempData.df_tasktype = df_temp

    def init_combo_type(self, cb):
        if self.table_type == 'contractor':
            data = self.tempData.df_contractortype  # 기업분류
        elif self.table_type == 'contact':
            data = self.tempData.df_contractor  # 소속업체
        elif self.table_type == 'country':
            data = self.tempData.df_region   # 지역
        elif self.table_type == 'tasktype':
            data = self.tempData.df_tasktype  # 지역
        for index, row in data.iterrows():
            newIndex = cb.count()
            cb.addItem(row['name'])
            cb.setItemData(newIndex, row['id'])

    def loadData(self):
        data = self.get_df()
        self.clearContents()
        self.setRowCount(0)
        for index, row in data.iterrows():
            new_row_index = self.rowCount()
            self.insertRow(new_row_index)
            self.initRowWidget(new_row_index)
            self.updateRow(new_row_index, row)

    def initRowWidget(self, row_index):
        check_box = QCheckBox()
        check_box.setStyleSheet("margin-left:10px;")
        self.setCellWidget(row_index, 0, check_box)
        if self.table_type == 'contractor':
            combo_box = QMyComboBox()
            self.init_combo_type(combo_box)
            self.setCellWidget(row_index, 3, combo_box)  # 사업자 유형
        elif self.table_type == 'contact':
            combo_box = QMyComboBox()
            combo_box.setEditable(True)
            self.init_combo_type(combo_box)
            self.setCellWidget(row_index, 3, combo_box)  # 소속
            date_edit = QDateEdit(calendarPopup=True)
            self.setCellWidget(row_index, 7, date_edit)  # 갱신날짜
        elif self.table_type == 'country':
            combo_box = QMyComboBox()
            self.init_combo_type(combo_box)
            self.setCellWidget(row_index, 3, combo_box)  # 지역코드

    def updateRow(self, row_index, row):
        self.setItem(row_index, 1, GetColItem(row['id'], True, True))
        self.setItem(row_index, 2, GetColItem(row['name']))
        if self.table_type == 'contractor':
            df_temp = self.tempData.df_project_contractor
            reference_counter = len(df_temp[df_temp['contractor_id'] == row['id']].index) #사업자와 연결된 회수
            df_temp = self.tempData.df_contact
            reference_counter += len(df_temp[df_temp['contractor_id'] == row['id']].index) #연락처와 연결된 회수
            combo_box = self.cellWidget(row_index, 3)
            combo_box.setCurrentIndex(combo_box.findData(int(row['type'])))
            self.setItem(row_index, 4, GetColItem(row['businessnumber']))
            self.setItem(row_index, 5, GetColItem(row['corporatenumber']))
            self.setItem(row_index, 6, GetColItem(reference_counter, False, True))
        elif self.table_type == 'contact':
            combo_box = self.cellWidget(row_index, 3)
            combo_box.setCurrentIndex(combo_box.findData(row['contractor_id']))
            self.setItem(row_index, 4, GetColItem(row['phone']))
            self.setItem(row_index, 5, GetColItem(row['email']))
            self.setItem(row_index, 6, GetColItem(row['address']))
            update_date = self.cellWidget(row_index, 7)
            update_date.setDate(QDate.fromString(row['updatedate'], Qt.ISODate))
        elif self.table_type == 'fundtype':
            df_temp = self.tempData.df_project_fund
            reference_counter = len(df_temp[df_temp['fundtype_id'] == row['id']].index)  # 사업과 연결된 회수
            self.setItem(row_index, 3, GetColItem(reference_counter, False, True))
        elif self.table_type == 'country':
            df_temp = self.tempData.df_project_country
            reference_counter = len(df_temp[df_temp['country_id'] == row['id']].index)  # 사업과 연결된 회수
            combo_box = self.cellWidget(row_index, 3)
            combo_box.setCurrentIndex(combo_box.findData(int(row['region_id'])))
            self.setItem(row_index, 4, GetColItem(reference_counter, False, True))
        elif self.table_type == 'region':
            df_temp = self.tempData.df_country
            reference_counter = len(df_temp[df_temp['region_id'] == row['id']].index)  # 국가와 연결된 회수
            self.setItem(row_index, 3, GetColItem(reference_counter, False, True))
        elif self.table_type == 'contractortype':
            df_temp = self.tempData.df_contractor
            reference_counter = len(df_temp[df_temp['type'] == row['id']].index)  # 사업과 연결된 회수
            self.setItem(row_index, 3, GetColItem(reference_counter, False, True))
        elif self.table_type == 'tasktype':
            df_temp = self.tempData.df_project_tasktype
            reference_counter = len(df_temp[df_temp['tasktype_id'] == row['id']].index)  # 사업과 연결된 회수
            self.setItem(row_index, 3, GetColItem(reference_counter, False, True))

    def add_new_row(self):
        new_row_index = self.rowCount()
        new_id = 0
        # 데이터 초기설정
        df_temp = self.get_df()
        # 새로운 ID 구하기
        if len(df_temp['id'].index) > 0:
            new_id = df_temp['id'].max() + 1
        # 컬럼 설정
        if self.table_type == 'contractor':
            values = {'id': new_id, 'name': '', 'type': 0, 'businessnumber': '', 'corporatenumber': ''}
            types = {'id': np.int, 'type': np.int}
        elif self.table_type == 'contact':
            values = {'id': new_id, 'name': '', 'phone': '', 'email': '', 'address': '',
                      'contractor_id': 0, 'updatedate':QDate.currentDate().toString(Qt.ISODate)}
            types = {'id': np.int, 'contractor_id': np.int}
        elif self.table_type == 'fundtype' or self.table_type == 'region' or self.table_type == 'contractortype' or self.table_type == 'tasktype' :
            values = {'id': new_id, 'name': ''}
            types = {'id': np.int}
        elif self.table_type == 'country':
            values = {'id': new_id, 'name': '', 'region_id': 0}
            types = {'id': np.int, 'region_id': np.int}
        # 데이터 추가 및 반영
        df_temp = df_temp.append(values, ignore_index=True).astype(types)
        self.set_df(df_temp)
        # UI에 표시하기
        self.insertRow(new_row_index)
        self.initRowWidget(new_row_index)
        row = df_temp[df_temp['id'] == new_id].iloc[0]
        self.updateRow(new_row_index, row)

    def delete_row(self):
        #삭제 경고문 출력
        ret = QMessageBox.question(self, '사업자 삭제', '체크된 항목을 정말로 삭제하시겠습니까?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.No:
            return
        df_temp = self.get_df()
        warning_text = ''
        for row_index in range(self.rowCount()-1, -1, -1):
            check_box = self.cellWidget(row_index, 0)
            bool_delete = check_box.isChecked()
            if bool_delete == True:
                # 다른 데이터에서 참조되고 있는 값의 경우 삭제하지 않음
                ref_counter_col = {'contractor': 6, 'contact': -1, 'fundtype': 3, 'country': 4, 'region': 3, 'contractortype': 3, 'tasktype': 3}
                if ref_counter_col != -1:
                    if int(self.item(row_index, ref_counter_col[self.table_type]).text()) > 0:
                        bool_delete = False
                        warning_text = "다른 테이블에서 참조하는 항목은 삭제할 수 없습니다."
            if bool_delete == True:
                index = df_temp.query('id == {}'.format(int(self.item(row_index, 1).text()))).index
                df_temp.drop(index, inplace=True)
                self.removeRow(row_index)
        self.set_df(df_temp)
        if warning_text != '':
            ShowWarning(self, warning_text)

    def update_df(self, df_update):
        if self.table_type == 'contractor':
            self.tempData.df_contractor.set_index('id', inplace=True)
            self.tempData.df_contractor.update(df_update.set_index('id'))
            self.tempData.df_contractor.reset_index(inplace=True)
            self.projectData.df_contractor = self.tempData.df_contractor
        elif self.table_type == 'contact':
            self.tempData.df_contact.set_index('id', inplace=True)
            self.tempData.df_contact.update(df_update.set_index('id'))
            self.tempData.df_contact.reset_index(inplace=True)
            self.projectData.df_contact = self.tempData.df_contact
        elif self.table_type == 'fundtype':
            self.tempData.df_fundtype.set_index('id', inplace=True)
            self.tempData.df_fundtype.update(df_update.set_index('id'))
            self.tempData.df_fundtype.reset_index(inplace=True)
            self.projectData.df_fundtype = self.tempData.df_fundtype
        elif self.table_type == 'country':
            self.tempData.df_country.set_index('id', inplace=True)
            self.tempData.df_country.update(df_update.set_index('id'))
            self.tempData.df_country.reset_index(inplace=True)
            self.projectData.df_country = self.tempData.df_country
        elif self.table_type == 'region':
            self.tempData.df_region.set_index('id', inplace=True)
            self.tempData.df_region.update(df_update.set_index('id'))
            self.tempData.df_region.reset_index(inplace=True)
            self.projectData.df_region = self.tempData.df_region
        elif self.table_type == 'contractortype':
            self.tempData.df_contractortype.set_index('id', inplace=True)
            self.tempData.df_contractortype.update(df_update.set_index('id'))
            self.tempData.df_contractortype.reset_index(inplace=True)
            self.projectData.df_contractortype = self.tempData.df_contractortype
        self.changed = True

    def apply_change(self):
        # 먼저 모든 값이 정상인지 Validate
        df_update = None
        for row_index in range(self.rowCount()):
            id = int(self.item(row_index, 1).text())
            name = self.item(row_index, 2).text()
            if name.strip() == '':
                ShowWarning(self, "{}번 줄에 항목 이름이 비어 있습니다.".format(row_index + 1))
                return
            if self.table_type == 'contractor':
                type = int(self.cellWidget(row_index, 3).currentData())
                businessnumber = self.item(row_index, 4).text()
                corporatenumber= self.item(row_index, 5).text()
                df_temp = pd.DataFrame({'id': [id], 'name': [name], 'type': [type], 'businessnumber': [businessnumber], 'corporatenumber': [corporatenumber]})
                if df_update is None:
                    df_update = df_temp
                else:
                    df_update = df_update.append(df_temp, ignore_index=True).astype({'id': np.int, 'type': np.int})
            elif self.table_type == 'contact':
                contractor_id = self.cellWidget(row_index, 3).currentData()
                if contractor_id is None:
                    ShowWarning(self, "{}번 줄에 소속이 지정되지 않았습니다.".format(row_index + 1))
                    return
                phone = self.item(row_index, 4).text()
                email = self.item(row_index, 5).text()
                address = self.item(row_index, 6).text()
                updatedate = self.cellWidget(row_index, 7).date().toString(Qt.ISODate)
                df_temp = pd.DataFrame({'id': [id], 'contractor_id': [contractor_id], 'name': [name], 'phone': [phone],
                                        'email': [email], 'address': [address], 'updatedate': [updatedate]})
                if df_update is None:
                    df_update = df_temp
                else:
                    df_update = df_update.append(df_temp, ignore_index=True).astype({'id': np.int, 'contractor_id': np.int})
            elif self.table_type == 'country':
                region_id = self.cellWidget(row_index, 3).currentData()
                df_temp = pd.DataFrame({'id': [id], 'name': [name], 'region_id': [region_id]})
                if df_update is None:
                    df_update = df_temp
                else:
                    df_update = df_update.append(df_temp, ignore_index=True).astype({'id': np.int, 'region_id': np.int})
            elif self.table_type == 'fundtype' or self.table_type == 'region' or self.table_type == 'contractortype' or self.table_type == "tasktype":
                df_temp = pd.DataFrame({'id': [id], 'name': [name]})
                if df_update is None:
                    df_update = df_temp
                else:
                    df_update = df_update.append(df_temp, ignore_index=True).astype({'id': np.int})
            else:
                return
        self.update_df(df_update)
        ShowWarning(self, '변경사항이 반영되었습니다.')

class ModalEditorDialog(QDialog):
    def __init__(self, parent, table_type):
        super().__init__()
        self.projectData = parent.projectData
        self.table_type = table_type
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon('db.png'))
        self.ui_list = ModalEditorTableWidget(self, self.table_type)
        #
        self.ui_add = QPushButton('새 항목 추가')
        self.ui_add.setMinimumHeight(30)
        self.ui_add.clicked.connect(self.event_btn_add)
        #
        self.ui_delete = QPushButton('체크된 항목 삭제')
        self.ui_delete.setMinimumHeight(30)
        self.ui_delete.clicked.connect(self.event_btn_delete)
        #
        self.ui_apply = QPushButton('변경사항 적용')
        self.ui_apply.setMinimumHeight(30)
        self.ui_apply.clicked.connect(self.event_btn_apply)
        #
        self.ui_close = QPushButton('닫기')
        self.ui_close.setMinimumHeight(30)
        self.ui_close.clicked.connect(self.event_btn_close)
        #
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.ui_list, 0, 0, 1, 5)
        grid.addWidget(self.ui_add, 1, 0, 1, 1)
        grid.addWidget(self.ui_delete, 1, 1, 1, 1)
        grid.addWidget(self.ui_apply, 1, 3, 1, 1)
        grid.addWidget(self.ui_close, 1, 4, 1, 1)
        self.resize(600, 320)
        if self.table_type == 'contractor':
            self.setWindowTitle('사업자 목록')
        elif self.table_type == 'contact':
            self.setWindowTitle('사업자 연락처')
        elif self.table_type == 'fundtype':
            self.setWindowTitle('자금 유형')
        elif self.table_type == 'tasktype':
            self.setWindowTitle('자금 유형')
        elif self.table_type == 'country':
            self.setWindowTitle('국가 목록')
        elif self.table_type == 'region':
            self.setWindowTitle('지역 구분')
        elif self.table_type == 'contractortype':
            self.setWindowTitle('기업 분류')
        else:
            self.setWindowTitle('알 수 없음')
        self.ui_close.setDefault(True)

    def event_btn_add(self):
        self.ui_list.add_new_row()

    def event_btn_delete(self):
        self.ui_list.delete_row()
        return

    def event_btn_apply(self):
        self.ui_list.apply_change()
        return

    def event_btn_close(self):
        self.close()
        return

    def is_changed(self):
        return self.ui_list.changed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myMain = MyMain()
    sys.exit(app.exec_())

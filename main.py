# Standart libraries
import configparser
import os
import sys
import random
import tempfile
import webbrowser

# Related libraries
import numpy as np
import pandas as pd
from astroquery.vizier import Vizier
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Local libraries
from convert_dates import *
from stars_plots import built_plots
from ui.gcvs import Ui_GCVS
from ui.queryData import Ui_QueryData
from ui.about import Ui_About
from ui.mainUI import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Initialize the UI 
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set up class variables
        self.undoStack = []
        self.win_star_chart = StarChart(self)
        self.HRDialog = HRDDialog(self)
        self.original_data = None
        self.starName = self.ui.comboBox.currentText()
        self.filename = ''

        # Start point
        self.begin()

        # Set up widgets connections
        self.ui.pushButton.clicked.connect(self.built_curve)
        self.ui.pushButton_2.clicked.connect(self.find_object)
        self.ui.lineEdit_2.returnPressed.connect(self.find_object)
        self.ui.comboBox.activated[str].connect(self.on_activated)
        self.ui.checkBox.stateChanged.connect(self.on_checkbox_state_changed)
        
        # Set up context menu for table
        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set up menu bar buttons connections
        self.ui.actionAAVSO.triggered.connect(lambda: self.info_AAVSO())
        self.ui.actionAbout.triggered.connect(lambda: self.open_about())
        self.ui.actionCopy.triggered.connect(lambda: self.copy_cells())
        self.ui.actionGCVS5.triggered.connect(lambda: self.open_GCVS())
        self.ui.actionHow_do_Observation.triggered.connect(lambda: self.info_how())
        self.ui.actionHRD.triggered.connect(lambda: self.on_hrd_triggered())
        self.ui.actionCalculate_Light_Intensity.triggered.connect(lambda: self.open_light_intensity())
        self.ui.actionVSInfo.triggered.connect(lambda:self.vs_char_info())
        self.ui.actionDiagram.triggered.connect(lambda: self.on_hrd_triggered())
        self.ui.actionVSX.triggered.connect(lambda: self.open_vsx())   
        self.ui.actionNew.triggered.connect(lambda: self.on_new_triggered())
        self.ui.actionOpen.triggered.connect(lambda: self.open_file(False))
        self.ui.actionPaste.triggered.connect(lambda: self.paste_cells())
        self.ui.actionSave.triggered.connect(lambda: self.on_save())
        self.ui.actionSave_As.triggered.connect(lambda: self.save_file())
        self.ui.actionStar_Chart.triggered.connect(lambda: self.show_star_chart())
        self.ui.actionExit.triggered.connect(lambda: self.close())
       
    def begin(self):
        # Load the list of stars from a file and add them to the combo box
        with open('ui/res/stars_list.txt', 'r') as file:
            self.stars = file.readlines()
        for option in self.stars:
            self.ui.comboBox.addItem(option.strip())
        
        # Load the list of databases from a file and add them to the combo box
        with open('ui/res/databases_list.txt', 'r') as file:
            dblist = file.readlines()
        for option in dblist:
            self.ui.comboBox_2.addItem(option.strip())

        # Load the settings and update the UI
        always, filename, starname = self.load_settings()
        self.ui.checkBox.setChecked(always)
        if always and filename:
            self.ui.plainTextEdit.insertPlainText(f"Has been started with current file: {filename}\n\n")
            self.ui.comboBox.setCurrentText(starname)
            self.on_activated(starname)
           
            # Load the data from the specified file
            _,file_extension = os.path.splitext(filename)
            if file_extension == '.txt':
                data = np.genfromtxt(file, filling_values=0)
                if data.shape[1] < 3:
                    data = np.hstack(
                        [data, np.zeros((data.shape[0], 3 - data.shape[1]))])
                    time = data[:, 0]
                    magnitude = data[:, 1]
                    errormag = data[:, 2]
                    time = pd.Series(time, name="t",  dtype=float)
                    magnitude = pd.Series(magnitude, name="mag", dtype=float)
                    errormag = pd.Series(errormag, name="magerr", dtype=float)
                    data = pd.concat([time, magnitude, errormag], axis=1)
                    
            elif file_extension == '.csv':
                data = pd.read_csv(filename)

                # Store the original data for later use
                self.original_data = data
                
            # Write the data to the table
            self.write_table(self.original_data)
             
    def show_star_chart(self):  
           self.win_star_chart.show()

    def info_how(self):
        url = 'https://www.aavso.org/tutorials' 
        webbrowser.open(url)

    def info_AAVSO(self):
        url = 'https://www.aavso.org/' 
        webbrowser.open(url)
    
    def open_vsx(self):
        url = 'https://www.aavso.org/vsx/index.php?view=search.top' 
        webbrowser.open(url)

    def open_about(self):
        self.about = About()
        self.about.show()

    def open_light_intensity(self):
        self.intent = LightIntensity()
        self.intent.show()

    def on_hrd_triggered(self):
        # Show the HRD dialog
        self.HRDialog.show()

    def vs_char_info(self):
        # Load the list of stars from a file and add them to the combo box
        with open('ui/res/variables_chars.txt', 'r',encoding='utf-8') as file:
           text = file.read()
        self.write_log(text)

    def save_settings(self, always, filename, starname):
        config = configparser.ConfigParser()
        config['Settings'] = {'ALWAYS': always,'FILENAME': filename, 'STARNAME': starname}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    def on_checkbox_state_changed(self, state):
        always = state == Qt.Checked
        self.save_settings(always, self.filename, self.starName)

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('ui/res/settings.ini')
        always = config.getboolean('Settings', 'ALWAYS', fallback=False)
        filename = config.get('Settings', 'FILENAME', fallback='')
        starname = config.get('Settings', 'STARNAME', fallback='')
        return always, filename, starname

    def show_context_menu(self, pos):
        context_menu = QtWidgets.QMenu(self)

        # Set context menu buttons
        copy_action = context_menu.addAction("Copy")
        paste_action = context_menu.addAction("Paste")
        delete_action = context_menu.addAction("Delete All")
        select_action = context_menu.addAction("Select All")
        add_row_action = context_menu.addAction("Add a row +")

        # Connect methods to the buttons
        copy_action.triggered.connect(self.copy_cells)
        paste_action.triggered.connect(self.paste_cells)
        delete_action.triggered.connect(self.delete_all)
        select_action.triggered.connect(self.select_all)
        add_row_action.triggered.connect(self.add_row)

        # Show context menu
        context_menu.exec_(QtGui.QCursor.pos())

    def copy_cells(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if selected_items:
            text = ''
            for item in selected_items:
                text += item.text() + '\t'
            QtWidgets.QApplication.clipboard().setText(text)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy()
            selected = self.selectedItems()
            if selected:
                text = selected[0].text()
                QtWidgets.QApplication.clipboard().setText(text)
        elif event.matches(QtGui.QKeySequence.Undo):
            if self.undoStack:
                row, column, text = self.undoStack.pop()
                self.item(row, column).setText(text)
        elif event.matches(QtGui.QKeySequence.Paste):
                self.paste_cells()
        else:
            super().keyPressEvent(event)

    def cellChanged(self, row, column):
        item = self.item(row, column)
        if item:
            currentText = item.text()
            self.undoStack.append((row, column, currentText))
        super().cellChanged(row, column)

    def paste_cells(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if selected_items:
            text = QtWidgets.QApplication.clipboard().text()
        rows = text.split('\n')
        if len(rows) > 1:
            for i, item in enumerate(selected_items):
                item.setText(rows[i])
        else:
            cols = text.split('\t')
            for i, item in enumerate(selected_items):
                item.setText(cols[i])

    def delete_all(self):
        self.ui.tableWidget.setRowCount(0) 

    def select_all(self):
        self.ui.tableWidget.selectAll()

    def add_row(self):
        # Get the last row`s position and add a row
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)
        self.write_log(f"Added a new {row_position+1}-row")
        starname = self.ui.comboBox.currentText()
        # Copy data from the last to the new row
        self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(starname))
        now = datetime.now()
        self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(now.strftime('%Y-%m-%d')))
        self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(now.hour)))
        self.ui.tableWidget.setItem(row_position, 3, QTableWidgetItem(str(now.minute)))
        self.ui.tableWidget.setItem(row_position, 4, QTableWidgetItem('1.1'))
        self.ui.tableWidget.setItem(row_position, 5, QTableWidgetItem('0.0'))
        self.ui.tableWidget.setItem(row_position, 6, QTableWidgetItem('0.0'))
        self.ui.tableWidget.setItem(row_position, 7, QTableWidgetItem('0.0'))
        
    def on_activated(self, text):
        self.starName = self.ui.comboBox.currentText()
        for i in range(0, len(self.stars)):
            self.ui.tableWidget.setItem(
                i, 0, QTableWidgetItem(self.starName))

    def on_new_triggered(self):
        # Clear the QTableWidget
        self.ui.tableWidget.setRowCount(0)
        
        # Set the current index of the QComboBox to the first item
        self.ui.comboBox.setCurrentIndex(0)
    
        # Clear the QPlainTextEdit
        self.ui.plainTextEdit.clear()

    def built_curve(self):
        data = self.get_table_data()

        time = data['t']
        magnitude = data['mag']
        errormag = data['magerr']

        period, amplitude = built_plots(time, magnitude, errormag, self.starName)
        self.write_log(f"Revealed Periodic Behavior:\nPeriod = {round(period,4)} hours and Amplitude = {round(amplitude,4)}")

    def get_table_data(self):
        # Initialize lists to store the extracted values
        time = []
        magnitude = []
        errormag = []

        # Extract the values from the table
        for row in range(self.ui.tableWidget.rowCount()):
            # Check if the date and time cells are not empty and contain valid data
            if (self.ui.tableWidget.item(row, 1) and self.ui.tableWidget.item(row, 2) and self.ui.tableWidget.item(row, 3)):
                try:
                    # Convert the date and time to a datetime object
                    date = datetime.strptime(self.ui.tableWidget.item(row, 1).text(), "%Y-%m-%d")
                    h = int(self.ui.tableWidget.item(row, 2).text())
                    m = int(self.ui.tableWidget.item(row, 3).text())

                    # Convert the datetime object to MJD and append it to the list
                    time.append(Gregorian_to_MJD(date, h, m))
                except ValueError:
                    self.write_log(f"Error: Invalid data in row {row + 1}")
                    return

            # Check if the magnitude cell is not empty and contains a valid float value
            if self.ui.tableWidget.item(row, 4):
                try:
                    magnitude_value = float(self.ui.tableWidget.item(row, 4).text())
                    magnitude.append(magnitude_value)
                except ValueError:
                    self.write_log(f"Error: Invalid data in row {row + 1}")
                    return

            # Check if the error cell is not empty and contains a valid float value
            if self.ui.tableWidget.item(row, 7):
                try:
                    errormag_value = float(self.ui.tableWidget.item(row, 7).text())
                    errormag.append(errormag_value)
                except ValueError:
                    self.write_log(f"Error: Invalid data in row {row + 1}")
                    return

        # Convert the lists to pandas Series
        time = pd.Series(time, name="t", dtype=float)
        magnitude = pd.Series(magnitude, name="mag", dtype=float)
        errormag = pd.Series(errormag, name="magerr", dtype=float)
   
        # Check if all three lists have the same length
        if len(time) == len(magnitude) == len(errormag):
            # Concatenate the Series into a DataFrame and return it
            data = pd.concat([time, magnitude, errormag], axis=1)
            return data
        else:
            self.write_log("Error: The time, magnitude, and errormag lists have different lengths")
            return

    def check_empty_cells(self):
        if not self.writing_mode:
            for row in range(self.ui.tableWidget.rowCount()):
                for col in range(self.ui.tableWidget.columnCount()):
                    if not self.ui.tableWidget.item(row, col):
                        self.write_log(f"Error: Empty cell found [{row+1};{col+1}]")
                        return

    def write_table(self, data):
        self.writing_mode = True
        # Set the number of rows in the table
        self.ui.tableWidget.setRowCount(data.shape[0])

        # Clear the contents of the table
        self.ui.tableWidget.clearContents()

        # Extract the values from the data
        results = self.data_to_values(data)

        # Write the values to the table
        for i in range(0, data.shape[0]):

            date = results[0][i]
            hour = results[1][i]
            minute = results[2][i]
            mag = results[3][i]
            magerr = results[4][i]

            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.starName))  # Star
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(str(date)))  # Date
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(str(hour)))  # Hour
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(str(minute)))  # Minute
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(str(mag)))  # Magnitude
            self.ui.tableWidget.setItem(i, 5, QTableWidgetItem(str('0.0')))  # Comp1
            self.ui.tableWidget.setItem(i, 6, QTableWidgetItem(str('0.0')))  # Comp2
            self.ui.tableWidget.setItem(i, 7, QTableWidgetItem(str(magerr)))  # ErrorMag
        self.writing_mode = False

    def open_file(self,ignore_changes):
        if self.check_changes() or ignore_changes:
            # Show a file dialog to let the user choose a file
            self.filename = QFileDialog.getOpenFileName(self, 'Choose A File:', '', 'All(*);; CSV (*.csv);;Text Files (*.txt)')[0]

            if self.filename:
                # Load the data from the specified file
                file = self.filename
                self.ui.plainTextEdit.insertPlainText(f"The current file is open: {file}\n\n")
            
                _,file_extension = os.path.splitext(file)
                    
                if file_extension == '.txt':
                    data = np.genfromtxt(file, filling_values=0)
                    if data.shape[1] < 3:
                        errormag = 0.006
                        data = np.hstack([data, np.full((data.shape[0], 3 - data.shape[1]), errormag)])

                        time = data[:, 0]
                        magnitude = data[:, 1]
                        errormag = data[:, 2]
                        
                        time = pd.Series(time, name="t",  dtype=float)
                        magnitude = pd.Series(magnitude, name="mag", dtype=float)
                        errormag = pd.Series(errormag, name="magerr", dtype=float)
                        data = pd.concat([time, magnitude, errormag], axis=1)
                    
                        self.original_data = data
                        self.write_table(data)
                        
                elif file_extension == '.csv':
                    data = pd.read_csv(file)
                    self.original_data = data
                    self.write_table(data)   
                else:
                    # Show an error message if the file type is not supported
                    self.ui.plainTextEdit.insertPlainText(f"Error: Invalid file type ({file_extension}). Expected .txt/.csv formats.\n\n")
        else:
            reply = QMessageBox.question(self, 'Saving changes', "Do you want to save current changes?",
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                # Save the data and accept the close event
                self.save_file()
            elif reply == QMessageBox.No:
                self.open_file(True)   
            else:
                pass
                # Ignore the close event   

    def save_file(self):
        # Get data from table
        data = self.get_table_data()

        # Show a save dialog 
        self.filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "", "CSV Files (*.csv);;Text Files (*.txt)")

        # Save the file
        if self.filename:
            if self.filename.endswith('.csv'):
                data.to_csv(self.filename, index=False)
                self.ui.plainTextEdit.insertPlainText(f"File saved in: {self.filename}")

            elif self.filename.endswith('.txt'):
                data.to_csv(self.filename, index=False, sep='\t')
                self.ui.plainTextEdit.insertPlainText(f"File saved in: {self.filename}")

    def on_save(self):
        self.original_data = self.get_table_data()

    def find_object(self):
        # Get the search parameters from the UI
        input_text = self.ui.lineEdit_2.text()
        db = self.ui.comboBox_2.currentText()

        # Show a message to indicate that the search is in progress
        self.ui.plainTextEdit.insertPlainText("---SEARCHING---\n\n")
        QApplication.processEvents()

        # Parse the input text
        input_text = input_text.split(',')
        if len(input_text) > 1:
            object_name = input_text[0].strip()
            catalouge = input_text[1].strip()
            if catalouge.isdigit():
                catalouge = int(catalouge)
            
            # Query the Vizier database for the specified object and catalogue
            data = Vizier.query_object(object_name)

            # Show the results in a DataTable window
            self.window3 = DataTable(data[catalouge])
            wintitle = f"{object_name} Observations in {db.capitalize()}-{catalouge}"
            self.window3.setWindowTitle(wintitle)
            self.window3.show()

            # Write the results to the log
            self.write_log(f"Results of searching '{object_name}' in {db.capitalize()} catalogue (record-{catalouge}):\n\n")
            self.ui.plainTextEdit.verticalScrollBar().setValue(
                self.ui.plainTextEdit.verticalScrollBar().maximum())
      
        else:
            # Query the Vizier database for the specified object
            object_name = input_text
            catalouge = ''
            data = Vizier.query_object(object_name)

            # Write the results to the log
            result = f"Results of searching '{object_name}' in {db.capitalize()} catalogue:\n\n"
            self.write_log(result+str(data)+'\n\n')
            self.ui.plainTextEdit.verticalScrollBar().setValue(
                self.ui.plainTextEdit.verticalScrollBar().maximum())
    
    def open_GCVS(self):
        self.write_log('Please, wait. A large file is opening...')
        QApplication.processEvents()
        self.window4 = GCVSWindow()
        self.window4.setWindowTitle('GCVS-5 offline')
        self.window4.show()
        self.write_log('The file is ready to use')
    
    def data_to_values(self, data):
        # Drop rows with missing values
        data = data.dropna()

        # Initialize lists to store the extracted values
        date = []
        hour = []
        minute = []
        mag = []
        magerr = []
    
        # Get the current date
        today = datetime.today()

        # Extract the values from the data
        for i in range(0, data.shape[0]):
           # Check the time type and convert it to a datetime object
            time = data.t.get(i, default=today)
            time_type = len(str(int(time)))

            if time_type >= 5 or time_type == 0:
                time = MJD_to_Gregorian(time)
            else:
                time = JD_to_Gregorian(time)

            # Append the extracted values to the lists
            date.append(time.date())
            hour.append(time.hour)
            minute.append(time.minute)
            mag.append(data.mag.get(i))
            magerr.append(data.magerr.get(i))

        # Return the extracted values
        return date,hour,minute,mag,magerr
           
    def check_changes(self):
        
        # Get the current data from the table
        data1 = self.get_table_data()
    
        # Get the original data
        data2 = self.original_data
    
        # Extract the values from the data
        results1 = self.data_to_values(data1)
        results2 = self.data_to_values(data2)

        # Initialize a flag to indicate whether the data has changed
        equal = True

        # Check if the number of rows is the same
        if data1.shape[0] == data2.shape[0]:
            # Compare the values in each row
            for i in range(0, data1.shape[0]):

                dt1 = results1[0][i]
                h1 = results1[1][i]
                m1 = results1[2][i]
                mag1 = results1[3][i]
                ermag1 = results1[4][i]

                dt2 = results2[0][i]
                h2 = results2[1][i]
                m2 = results2[2][i]
                mag2 = results2[3][i]
                ermag2 = results2[4][i]

                # Adjust the minute value if necessary
                if abs(m1-m2) == 1:
                    m1 += 1

                # Check if any of the values have changed
                if dt1 != dt2 or h1 != h2 or m1 != m2 or mag1 != mag2 or ermag1 != ermag2:
                    equal = False
                    self.write_log(f"Row-{i+1} change detected:")
                    self.ui.plainTextEdit.insertPlainText(f"{dt2} -> {dt1}\n")
                    self.ui.plainTextEdit.insertPlainText(f"{h2} -> {h1}\n")
                    self.ui.plainTextEdit.insertPlainText(f"{m2} -> {m1}\n")
                    self.ui.plainTextEdit.insertPlainText(f"{mag2} -> {mag1}\n")
                    self.ui.plainTextEdit.insertPlainText(f"{ermag2} -> {ermag1}\n\n")
                    self.ui.plainTextEdit.verticalScrollBar().setValue(self.ui.plainTextEdit.verticalScrollBar().maximum())
        else:
            equal = False

        # Return whether the data has changed
        return equal

    def write_log(self,text):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.ui.plainTextEdit.insertPlainText(f"[{current_time}] \n")
        self.ui.plainTextEdit.insertPlainText(text+"\n\n")
        self.ui.plainTextEdit.verticalScrollBar().setValue(self.ui.plainTextEdit.verticalScrollBar().maximum())

    def closeEvent(self, event):
        # Check if the data has changed
        equal = self.check_changes()
       
        # If the data has changed, ask the user if they want to save it
        if self.original_data is not None:
            if not equal:
                reply = QMessageBox.question(self, 'Saving changes', "Do you want to save current changes?",
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    # Save the data and accept the close event
                    self.save_file()
                    event.ignore()       
                elif reply == QMessageBox.No:
                    # Accept the close event without saving
                    event.accept()  
                elif reply == QMessageBox.Cancel:
                    # Ignore the close event
                    event.ignore()

class RotatebleLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        # Initialize the label and set the pixmap
        super().__init__(*args, **kwargs)
        self.angle = 0
        self.pixmap = QtGui.QPixmap("ui/res/Star Chart.png")
        self.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        # Record the starting position of the mouse when the left button is pressed
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        # Rotate the pixmap when the left mouse button is held down and moved
        if event.buttons() & QtCore.Qt.LeftButton:
            center = QtCore.QPoint(int(self.width() / 2),
                                   int(self.height() / 2))
            start_angle = QtCore.QLineF(
                center, self.mapFromParent(self.start_pos)).angle()
            current_angle = QtCore.QLineF(
                center, self.mapFromParent(event.pos())).angle()
            delta_angle = start_angle - current_angle
            self.angle += delta_angle
            t = QtGui.QTransform().translate(center.x(), center.y()).rotate(
                self.angle).translate(-center.x(), -center.y())
            self.setPixmap(self.pixmap.transformed(t))
            self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        # Clear the starting position of the mouse when the left button is released
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = None

class StarChart(QtWidgets.QDialog):
    def __init__(self,parent=None):
        # Initialize the UI and create a RotatebleLabel
        super(StarChart, self).__init__(parent, QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setModal(False)
        # self.ui = Ui_StarChart()cd
        # self.ui.setupUi(self)
        self.resize(989, 1007)
        self.setWindowTitle("Star Chart")
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color:rgb(0, 0, 0)")
        self.label = RotatebleLabel(self)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))

        # Center the window on the screen
        self.centerOnScreen()

    def centerOnScreen(self):
        # Move the window to the center of the screen
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move(int(resolution.width()/2)-33, 0)

class GCVSWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Initialize the UI and set the data
        super().__init__()
        self.ui = Ui_GCVS()
        self.ui.setupUi(self)
        self.load_data()
        # Set up widgets connections
        self.ui.pushButton.clicked.connect(self.search_table)
        self.ui.lineEdit.returnPressed.connect(self.search_table)
        self.ui.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.table.customContextMenuRequested.connect(self.show_context_menu)

    def search_table(self):
        searchText = self.ui.lineEdit.text().replace(' ', '').lower()
        self.ui.table.clearSelection()
 
        for row in range(self.ui.table.rowCount()):
            for column in range(self.ui.table.columnCount()):
                item = self.ui.table.item(row, column)
                if item and item.text().replace(' ', '').lower() == searchText:
                    self.ui.table.selectRow(row)
                    self.ui.table.scrollToItem(item)
                    self.ui.table.horizontalScrollBar().setValue(0)
                    return

    def load_data(self):
        # Set the filename and column names
        filename = 'stars/gcvs5.txt' 
        column_names = ['ID', 'GCVS Name','J2000.0 Coordinates','Type of Variability1','Visual Magnitude','Absolute Magnitude','col-7','Epoch','Period of Variabilit','col-10','Amplitude','Rise Time','Spectrum','Other Catalogs','col-15','Galactic Coordinates','col-17','col-18','Catalog Name','Type of Variability2','GCVS Nam','col-22','col-23']

        # Find the maximum number of fields in the file
        max_fields = 0
        with open(filename, 'r') as f:
            for line in f:
                max_fields = max(max_fields, len(line.split('|')))

        # Create a temporary file and write the modified lines to it
        with tempfile.NamedTemporaryFile(mode='w',delete=False) as f_temp:
            with open(filename, 'r') as f:
                for line in f:
                    fields = line.rstrip().split('|')
                    fields += [''] * (max_fields - len(fields))
                    f_temp.write('|'.join(fields) + '\n')
            temp_filename = f_temp.name

        # Read the temporary file into a DataFrame
        data = pd.read_csv(temp_filename, sep='|', names=column_names)
        os.unlink(temp_filename)    

        # Set the table sizes  
        self.ui.table.setRowCount(data.shape[0])
        self.ui.table.setColumnCount(data.shape[1])
        self.ui.table.setHorizontalHeaderLabels(column_names)

        # Write the data to the table
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                self.ui.table.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))
    
    def show_context_menu(self, pos):
        context_menu = QtWidgets.QMenu(self)
        copy_action = context_menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_cells)
        paste_action = context_menu.addAction("Paste")
        paste_action.triggered.connect(self.paste_cells)
        context_menu.exec_(QtGui.QCursor.pos())

    def copy_cells(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if selected_items:
            text = ''
            for item in selected_items:
                text += item.text() + '\t'
            QtWidgets.QApplication.clipboard().setText(text)

class DataTable(QtWidgets.QMainWindow):
    def __init__(self, data):
        # Initialize the UI and set the data
        super().__init__()
        self.ui = Ui_QueryData()
        self.ui.setupUi(self)
        self.set_data(data)

        # Set up the context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        # Create the context menu and add actions
        context_menu = QtWidgets.QMenu(self)
        copy_action = context_menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_cells)
        paste_action = context_menu.addAction("Paste")
        paste_action.triggered.connect(self.paste_cells)

        # Show the context menu
        context_menu.exec_(QtGui.QCursor.pos())

    def copy_cells(self):
        # Copy the selected cells to the clipboard
        selected_items = self.ui.table.selectedItems()
        if selected_items:
            text = ''
            for item in selected_items:
                text += item.text() + '\t'
            QtWidgets.QApplication.clipboard().setText(text)

    def paste_cells(self):
        # Paste the contents of the clipboard into the selected cells
        selected_items = self.ui.table.selectedItems()
        if selected_items:
            text = QtWidgets.QApplication.clipboard().text()
        rows = text.split('\n')
        if len(rows) > 1:
            for i, item in enumerate(selected_items):
                item.setText(rows[i])
        else:
            cols = text.split('\t')
            for i, item in enumerate(selected_items):
                item.setText(cols[i])

    def set_data(self, data):
        # Convert the data to a list of lists
        data_list = [list(row) for row in data]

        # Set the table sizes
        self.ui.table.setRowCount(len(data_list))
        self.ui.table.setColumnCount(len(data_list[0]))

        # Set the column names
        column_names = data.colnames
        self.ui.table.setHorizontalHeaderLabels(column_names)

        # Write the data to the table
        for row in range(len(data_list)):
            for col in range(len(data_list[row])):
                item = QtWidgets.QTableWidgetItem(str(data_list[row][col]))
                self.ui.table.setItem(row, col, item)

class HRDDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(HRDDialog, self).__init__(parent,  QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setModal(False)

        # Set the window title
        self.setWindowTitle("Hertzsprung-Russell Diagram")
        
        # Set the window background color
        self.setStyleSheet("background-color: rgb(157,180,255);")
        
        self.setCursor(QtCore.Qt.CrossCursor)
        # Create the left image label
        self.leftImageLabel = QtWidgets.QLabel()
        self.leftImageLabel.setPixmap(QtGui.QPixmap("ui/res/HRDiagram1.png"))
        self.leftImageLabel.setStyleSheet("background-color: black;")
        
        # Create the right image label
        self.rightImageLabel = QtWidgets.QLabel()
        self.rightImageLabel.setPixmap(QtGui.QPixmap("ui/res/HRDiagram2.png"))
        
        # Create the layout and add the image labels
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.leftImageLabel)
        layout.addWidget(self.rightImageLabel)
        # Center the window on the screen
        self.centerOnScreen()

    def centerOnScreen(self):
        # Get the window geometry
        windowGeometry = self.frameGeometry()
        
        # Get the screen resolution
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        
        # Calculate the center position
        centerX = int((resolution.width() - windowGeometry.width()) / 2-640)
        centerY = int((resolution.height() - windowGeometry.height()) / 2-420)
        
        # Move the window to the center position
        self.move(centerX, centerY)

class About(QtWidgets.QMainWindow):
    def __init__(self):
        # Initialize the UI 
        super().__init__()
        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.ui.aboutText.setOpenExternalLinks(True)
        self.ui.imageLabel.setPixmap(QtGui.QPixmap("ui/res/just.jpg"))
        self.ui.pushButton.clicked.connect(lambda: self.close())
        self.centerOnScreen() 
    
    def centerOnScreen(self):
      # Get the window geometry
        windowGeometry = self.frameGeometry()
        
        # Get the screen resolution
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        
        # Calculate the center position
        centerX = int((resolution.width() - windowGeometry.width()) / 2)
        centerY = int((resolution.height() - windowGeometry.height()) / 2)
        
        # Move the window to the center position
        self.move(centerX, centerY)

class LightIntensity(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui/Stars Beholder.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setWindowTitle("Light Intensity Plot")

        # Create label with text
        self.label = QtWidgets.QLabel("It`s random generated start data. You can change to yours:", self)

        # Create a new table
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setRowCount(100)
        self.table.setHorizontalHeaderLabels(["Wavelength", "Intensity"])
        self.table.setColumnWidth(0, 290)
        self.table.setColumnWidth(1, 290)
        self.table.setGridStyle(QtCore.Qt.DashLine)

        # Create button with connection
        self.button = QtWidgets.QPushButton("Plot", self)
        self.button.clicked.connect(self.plot)
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # Craete canvas
        self.canvas = FigureCanvas(Figure())

        # Put widgets on layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        layout.addWidget(self.canvas)
        self.generate_start_data()

    def generate_start_data(self):
        for row in range(self.table.rowCount()):
            wavelength = random.uniform(300, 800)
            intensity = random.uniform(0, 100)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(wavelength)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(intensity)))

    def plot(self):
        # Get table data
        data = []

        for row in range(self.table.rowCount()):
            wavelength = float(self.table.item(row, 0).text())
            intensity = float(self.table.item(row, 1).text())
            data.append((wavelength, intensity))

        # Sort wave by lenght
        data.sort(key=lambda x: x[0])

        # Divide to two list
        wavelengths = [x[0] for x in data]
        intensities = [x[1] for x in data]

        # Show the plot
        ax = self.canvas.figure.subplots()
        ax.clear()
        ax.plot(wavelengths, intensities, color='blue', linestyle='solid', linewidth=2, marker='o')
        ax.set_xlabel("Wavelength")
        ax.set_ylabel("Intensity")
        self.canvas.draw()

if __name__ == '__main__':
    # Create the QApplication
    app = QApplication(sys.argv)
 
    # Create and show the main window
    window = MainWindow()
    window.show()

    # Show the star chart window
    win_star_chart = StarChart(window)
    win_star_chart.show()
    
    # Run the event loop
    sys.exit(app.exec_())
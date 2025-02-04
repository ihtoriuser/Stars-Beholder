# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(688, 340)
        About.setMinimumSize(QtCore.QSize(688, 340))
        About.setStyleSheet("background-color:black;")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ui/Stars Beholder.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        About.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(About)
        self.centralwidget.setObjectName("centralwidget")
        self.quote = QtWidgets.QLabel(self.centralwidget)
        self.quote.setGeometry(QtCore.QRect(270, 10, 401, 81))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setItalic(True)
        font.setKerning(False)
        self.quote.setFont(font)
        self.quote.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.quote.setStyleSheet("color:white;")
        self.quote.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.quote.setObjectName("quote")
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(20, 20, 212, 281))
        self.imageLabel.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.imageLabel.setStyleSheet("background-color:grey;")
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.aboutText = QtWidgets.QLabel(self.centralwidget)
        self.aboutText.setGeometry(QtCore.QRect(250, 100, 421, 191))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        self.aboutText.setFont(font)
        self.aboutText.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.aboutText.setStyleSheet("color:white;")
        self.aboutText.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.aboutText.setOpenExternalLinks(True)
        self.aboutText.setObjectName("aboutText")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(410, 300, 91, 23))
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setStyleSheet("color:balck; background-color:white;")
        self.pushButton.setObjectName("pushButton")
        About.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(About)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 688, 21))
        self.menubar.setObjectName("menubar")
        About.setMenuBar(self.menubar)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.quote.setText(_translate("About", "“The debt to our ancestors for the observations they made to our benefit,\n"
"we can pay only by doing the same for our ancestors”\n"
"\n"
"— Ejnar Hertzsprung, 1961"))
        self.aboutText.setText(_translate("About", "<html><head/><body><p>This application was created as a scientific work for study. It does not at all</p><p>pretend to be a professional tool for real astronomers. But the functionality </p><p>works. Designed for amateurs by an amateur! </p><p>Details:</p><p><br/>e-mail: <a href=\"ihtorius@gmail.com\"><span style=\" text-decoration: underline; color:#0000ff;\">ihtorius@gmail.com</span></a></p><p>Telegram: <a href=\"https://t.me/IHTORIUS\"><span style=\" text-decoration: underline; color:#0000ff;\">ihtorius</span></a></p><p>Ikhtiyor Bakhramov, 2023</p></body></html>"))
        self.pushButton.setText(_translate("About", "Close"))

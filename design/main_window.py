# Form implementation generated from reading ui file '.\ui\main_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1366, 720)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1366, 720))
        MainWindow.setMaximumSize(QtCore.QSize(1366, 720))
        MainWindow.setBaseSize(QtCore.QSize(1366, 720))
        MainWindow.setWindowTitle("Similarity")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/fractal-icon-8-removebg-preview.ico"), QtGui.QIcon.Mode.Active, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        MainWindow.setDocumentMode(True)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 881, 711))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.horizontalLayout2.setSpacing(2)
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.topLeftLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topLeftLabel.sizePolicy().hasHeightForWidth())
        self.topLeftLabel.setSizePolicy(sizePolicy)
        self.topLeftLabel.setMaximumSize(QtCore.QSize(480, 360))
        self.topLeftLabel.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.topLeftLabel.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.topLeftLabel.setText("")
        self.topLeftLabel.setPixmap(QtGui.QPixmap(".\\ui\\../TestImages/22.jpg"))
        self.topLeftLabel.setScaledContents(True)
        self.topLeftLabel.setWordWrap(False)
        self.topLeftLabel.setObjectName("topLeftLabel")
        self.horizontalLayout2.addWidget(self.topLeftLabel)
        self.topRightLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topRightLabel.sizePolicy().hasHeightForWidth())
        self.topRightLabel.setSizePolicy(sizePolicy)
        self.topRightLabel.setMaximumSize(QtCore.QSize(480, 360))
        self.topRightLabel.setText("")
        self.topRightLabel.setPixmap(QtGui.QPixmap(".\\ui\\../TestImages/22.jpg"))
        self.topRightLabel.setScaledContents(True)
        self.topRightLabel.setObjectName("topRightLabel")
        self.horizontalLayout2.addWidget(self.topRightLabel)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btmLeftLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btmLeftLabel.sizePolicy().hasHeightForWidth())
        self.btmLeftLabel.setSizePolicy(sizePolicy)
        self.btmLeftLabel.setMaximumSize(QtCore.QSize(480, 360))
        self.btmLeftLabel.setText("")
        self.btmLeftLabel.setPixmap(QtGui.QPixmap(".\\ui\\../TestImages/22.jpg"))
        self.btmLeftLabel.setScaledContents(True)
        self.btmLeftLabel.setObjectName("btmLeftLabel")
        self.horizontalLayout.addWidget(self.btmLeftLabel)
        self.btmRightLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btmRightLabel.sizePolicy().hasHeightForWidth())
        self.btmRightLabel.setSizePolicy(sizePolicy)
        self.btmRightLabel.setMaximumSize(QtCore.QSize(480, 360))
        self.btmRightLabel.setText("")
        self.btmRightLabel.setPixmap(QtGui.QPixmap(".\\ui\\../TestImages/22.jpg"))
        self.btmRightLabel.setScaledContents(True)
        self.btmRightLabel.setObjectName("btmRightLabel")
        self.horizontalLayout.addWidget(self.btmRightLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(900, 9, 451, 91))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(parent=self.groupBox)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(10, 20, 431, 31))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(128)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.startButton = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.startButton.setObjectName("startButton")
        self.horizontalLayout_3.addWidget(self.startButton)
        self.stopButton = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout_3.addWidget(self.stopButton)
        self.templateButton = QtWidgets.QPushButton(parent=self.groupBox)
        self.templateButton.setGeometry(QtCore.QRect(160, 60, 131, 24))
        self.templateButton.setObjectName("templateButton")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(900, 110, 451, 80))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(10, 20, 41, 16))
        self.label.setObjectName("label")
        self.labelSpeed = QtWidgets.QLabel(parent=self.groupBox_2)
        self.labelSpeed.setGeometry(QtCore.QRect(60, 20, 381, 16))
        self.labelSpeed.setObjectName("labelSpeed")
        self.labelUptime = QtWidgets.QLabel(parent=self.groupBox_2)
        self.labelUptime.setGeometry(QtCore.QRect(60, 40, 381, 16))
        self.labelUptime.setObjectName("labelUptime")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 41, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(10, 60, 41, 16))
        self.label_3.setObjectName("label_3")
        self.labelFps = QtWidgets.QLabel(parent=self.groupBox_2)
        self.labelFps.setGeometry(QtCore.QRect(60, 60, 381, 16))
        self.labelFps.setObjectName("labelFps")
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionExit.setObjectName("actionExit")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", "Control"))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.stopButton.setText(_translate("MainWindow", "STOP"))
        self.templateButton.setText(_translate("MainWindow", "Make Template"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Values"))
        self.label.setText(_translate("MainWindow", "Speed"))
        self.labelSpeed.setText(_translate("MainWindow", "0"))
        self.labelUptime.setText(_translate("MainWindow", "0"))
        self.label_2.setText(_translate("MainWindow", "Uptime"))
        self.label_3.setText(_translate("MainWindow", "FPS"))
        self.labelFps.setText(_translate("MainWindow", "0"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
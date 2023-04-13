



import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter,QColor,QFont,QPen
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import math
import socket
# from RodClass_copy import Rod
from Rod4client import Rod
from MultiPID import MultiPID


class RodWidget(QWidget):

    def __init__(self,rod):
        super().__init__()    
        # 摆杆下端点（原点）相对工作区的坐标(用于确定摆相对窗口的位置)
        self.__oriPoint = np.mat([self.geometry().width()*0.5 , self.geometry().height()*0.6]) 
        self.__rod = rod
        # self.__controller = ctrl
        # self.__AutoReset = True                      # 默认进行自动重置

        # 配置定时器，调用paintEvent刷新频率周期为1ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(5)


    
   
    # 开始绘制，周期5ms
    def startPaintRod(self):
        self.timer.start(5)
    
    # 停止绘制
    def stopPaintRod(self):
        self.timer.stop()

   
    # 绘制网格
    def drawGrid(self,painter,x,y):
        # 粗实线画X轴
        painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine))  
        painter.drawLine(QLineF(0 , y , self.geometry().width() , y))

        # 如果位移没有超过出屏，Y轴就用粗实线画，否则用细实线画
        if self.__rod.getX() > -self.geometry().width()/2 and self.__rod.getX() < self.geometry().width()/2:
            painter.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
            painter.drawLine(QLineF(x , 0 , x , self.geometry().height()))
        else:
            painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
            painter.drawLine(QLineF(x , 0 , x , self.geometry().height()))

        # 细实线画网格
        painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        temp1 = temp2 = y
        while(temp1 > 0):
            temp1 -= 30
            painter.drawLine(QLineF(0 , temp1 , self.geometry().width() , temp1))
        while(temp2 < self.geometry().height()):
            temp2 += 30
            painter.drawLine(QLineF(0 , temp2 , self.geometry().width() , temp2))
        
        temp1 = temp2 = x
        while(temp1 > 0):
            temp1 -= 30
            painter.drawLine(QLineF(temp1 , 0 , temp1 , self.geometry().height()))
        while(temp2 < self.geometry().width()):
            temp2 += 30
            painter.drawLine(QLineF(temp2 , 0 , temp2 , self.geometry().height()))

  

    # 摆杆绘制事件
    def paintEvent(self,event):
        # 重新适配原点y坐标位置
        self.__oriPoint = np.mat([self.geometry().width()*0.5 , self.geometry().height()*0.6]) 

        # 开始绘制
        painter = QPainter(self)
        # painter.begin(self)



                
        posTemp = self.__oriPoint.copy()
        posTemp[0,0] += self.__rod.getX()       #把摆杆下端点位移加上工作区中点坐标，写回rod.__pos，这样返回直线坐标时适配窗口拖动
        posTemp[0,0] %= self.geometry().width()
        self.__rod.setPos(posTemp)

        # 绘制坐标网格
        self.drawGrid(painter , self.__oriPoint[0,0] , self.__oriPoint[0,1])

        # 绘制摆杆
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))   #设置画笔颜色   
        rodLine = self.__rod.returnAsLine() 
        painter.drawLine(QLineF(rodLine[0,0],rodLine[0,1],rodLine[0,2],rodLine[0,3]))
        # 绘制小车
        painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))   #设置画笔颜色   
        painter.drawRect(int(rodLine[0,0]-50),int(rodLine[0,1]),100,50)
        # 绘制结束
        # painter.end()

class ThreadNetworkRecv(QThread):
    signal_recv_data= pyqtSignal(list)
    def __init__(self,socket_net):
        super().__init__()
        self.__socket_net = socket_net
        # test part start
        self.lastdata=""
        # test part end
        self.connected=False
    def run(self):
        global communication_flag,address # true is recv status,false is send status
        while True:
            # if communication_flag:
            while not self.connected:
                try:
                    self.__socket_net.connect(address)
                    self.connected=True
                except socket.error:
                    pass
            try:
                data=self.__socket_net.recv(1024).decode()
            except WindowsError:
                # sys.exit()
                pass
            # test part start
            # if(data !=self.lastdata):
            # print(data)
                # self.lastdata=data
            # test part end
            self.signal_recv_data.emit(string2list(data))# data: vector,velocity,angle,omega
            # print(data)
            communication_flag=False
class ThreadNetworkSend(QThread):
    def __init__(self,socket_net,pids):
        super().__init__()
        self.__socket_net = socket_net
        self.__pids = pids
        self.__data = [0,0,0,0]
    def setData(self,data):
        self.__data = data
    def run(self):
        # global communication_flag
        # if not communication_flag:
        cal_f=self.__pids.calculate(self.__data)
        # test part start
        # print(cal_f)
        # test part end
        self.__socket_net.send(str(cal_f).encode("utf-8"))
        communication_flag=True
class Ui_Form(QtWidgets.QWidget):
    def __init__(self,rod,path,pids) -> None:
        super().__init__()
        self.setupUi(self,rod)
        self.autoResetFlag=True
        self.__rod=rod
        self.pids=pids
        self.path=path
        self.__netRecv=ThreadNetworkRecv(path)
        self.__netSend=ThreadNetworkSend(path,pids)
        # todo:增加输入框事件和按钮事件链接
        self.__netRecv.signal_recv_data.connect(self.receiveData)
        self.__netRecv.start()
        # self.__netSend.start()
    def setupUi(self, Form,rod):
        Form.setObjectName("Form")
        Form.resize(870, 486)
        # todo: 增加四项pid输入框，默认值为零，及使能按钮

        self.gridLayout = QtWidgets.QGridLayout(Form)
        # self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setObjectName("gridLayout")

        self.rodWidget=RodWidget(rod)
        self.resetbutton=QtWidgets.QPushButton(self)
        
        # self.rodWidget.setObjectName("widget")
        self.rodWidget.setMinimumSize(QtCore.QSize(650, 400))
        self.gridLayout.addWidget(self.rodWidget, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.vector_p = QtWidgets.QLineEdit(Form)
        self.vector_p.setObjectName("vector_p")
        self.horizontalLayout.addWidget(self.vector_p)
        self.vector_i = QtWidgets.QLineEdit(Form)
        self.vector_i.setObjectName("vector_i")
        self.horizontalLayout.addWidget(self.vector_i)
        self.vector_d = QtWidgets.QLineEdit(Form)
        self.vector_d.setObjectName("vector_d")
        self.horizontalLayout.addWidget(self.vector_d)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.velocity_p = QtWidgets.QLineEdit(Form)
        self.velocity_p.setObjectName("velocity_p")
        self.horizontalLayout_2.addWidget(self.velocity_p)
        self.velocity_i = QtWidgets.QLineEdit(Form)
        self.velocity_i.setObjectName("velocity_i")
        self.horizontalLayout_2.addWidget(self.velocity_i)
        self.velocity_d = QtWidgets.QLineEdit(Form)
        self.velocity_d.setObjectName("velocity_d")
        self.horizontalLayout_2.addWidget(self.velocity_d)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.angle_p = QtWidgets.QLineEdit(Form)
        self.angle_p.setObjectName("angle_p")
        self.horizontalLayout_3.addWidget(self.angle_p)
        self.angle_i = QtWidgets.QLineEdit(Form)
        self.angle_i.setObjectName("angle_i")
        self.horizontalLayout_3.addWidget(self.angle_i)
        self.angle_d = QtWidgets.QLineEdit(Form)
        self.angle_d.setObjectName("angle_d")
        self.horizontalLayout_3.addWidget(self.angle_d)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.omega_p = QtWidgets.QLineEdit(Form)
        self.omega_p.setObjectName("omega_p")
        self.horizontalLayout_4.addWidget(self.omega_p)
        self.omega_i = QtWidgets.QLineEdit(Form)
        self.omega_i.setObjectName("omega_i")
        self.horizontalLayout_4.addWidget(self.omega_i)
        self.omega_d = QtWidgets.QLineEdit(Form)
        self.omega_d.setObjectName("omega_d")
        self.horizontalLayout_4.addWidget(self.omega_d)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.resetbutton)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.gridLayout.setColumnMinimumWidth(0, 5)
        self.gridLayout.setColumnMinimumWidth(1, 1)
        self.gridLayout.setColumnStretch(0, 5)
        self.gridLayout.setColumnStretch(1, 1)


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # signal slot set
        self.angle_p.editingFinished.connect(self.changePID)
        self.angle_i.editingFinished.connect(self.changePID)
        self.angle_d.editingFinished.connect(self.changePID)
        self.omega_p.editingFinished.connect(self.changePID)
        self.omega_i.editingFinished.connect(self.changePID)
        self.omega_d.editingFinished.connect(self.changePID)
        self.vector_p.editingFinished.connect(self.changePID)
        self.vector_i.editingFinished.connect(self.changePID)
        self.vector_d.editingFinished.connect(self.changePID)
        self.velocity_p.editingFinished.connect(self.changePID)
        self.velocity_i.editingFinished.connect(self.changePID)
        self.velocity_d.editingFinished.connect(self.changePID)
        self.resetbutton.clicked.connect(self.reset)
        # self.label.



    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "位  置 PID"))
        self.label_2.setText(_translate("Form", "速  度 PID"))
        self.label_3.setText(_translate("Form", "角  度 PID"))
        self.label_4.setText(_translate("Form", "角速度 PID"))
        self.vector_p.setText(_translate("Form", "0"))
        self.vector_i.setText(_translate("Form", "0"))
        self.vector_d.setText(_translate("Form", "0"))
        self.velocity_p.setText(_translate("Form", "0"))
        self.velocity_i.setText(_translate("Form", "0"))
        self.velocity_d.setText(_translate("Form", "0"))
        self.angle_p.setText(_translate("Form", "0"))
        self.angle_i.setText(_translate("Form", "0"))
        self.angle_d.setText(_translate("Form", "0"))
        self.omega_p.setText(_translate("Form", "0"))
        self.omega_i.setText(_translate("Form", "0"))
        self.omega_d.setText(_translate("Form", "0"))

    def changePID(self):
        # vector
        if self.sender()==self.vector_p:
            self.pids.PID_dispPos.setKP(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.vector_i:
            self.pids.PID_dispPos.setKI(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.vector_d:
            self.pids.PID_dispPos.setKD(-float(self.sender().text()) if self.sender().text()!="" else 0)
        # velocity
        elif self.sender()==self.velocity_p:
            self.pids.PID_dispSpd.setKP(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.velocity_i:
            self.pids.PID_dispSpd.setKI(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.velocity_d:
            self.pids.PID_dispSpd.setKD(-float(self.sender().text()) if self.sender().text()!="" else 0)
        # angle  
        elif self.sender()==self.angle_p:
            self.pids.PID_angPos.setKP(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.angle_i:
            self.pids.PID_angPos.setKI(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.angle_d:
            self.pids.PID_angPos.setKD(-float(self.sender().text()) if self.sender().text()!="" else 0)
        # omega
        elif self.sender()==self.omega_p:
            self.pids.PID_angSpd.setKP(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.omega_i:
            self.pids.PID_angSpd.setKI(-float(self.sender().text()) if self.sender().text()!="" else 0)
        elif self.sender()==self.omega_d:
            self.pids.PID_angSpd.setKD(-float(self.sender().text()) if self.sender().text()!="" else 0)

    def reset(self):
        self.path.send("reset".encode("utf-8"))
        self.pids.reset()

    def receiveData(self,data):
        # self.rodWidget.
        #picture update
        if self.autoResetFlag and (data[2]>90 or data[2] <-90):
            self.reset()
            # data=[0,0,0,0]
            return
        self.__rod.setData(data)
        #todo: pid process
        self.__netSend.setData(data)
        self.__netSend.start()


def string2list(s):
    # print("s:",s)
    res=s.strip('[')
    res=res.strip(']')
    res=res.replace(" ","")
    res=res.split(',')
    # print(res)
    res=[float(i) for i in res]
    # print(res)
    return res

if __name__ == "__main__":
    communication_flag=True
    app=QApplication(sys.argv)
    t = 0.001                          #计算周期
    rod = Rod(0.3,1,t)                  #创建一个摆杆信息储存对象
    # pids=MultiPID([0,0,0],[0,0,0],[0,0,0],[0,0,0])
    # init socket
    host = "localhost"
    port = 12345
    address = (host, int(port))
    path = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # path.connect(address)
    # init done
    pids=MultiPID(t,[0,0,0],[0,0,0],[0,0,0],[0,0,0])



    ui=Ui_Form(rod,path,pids)
    # print()
    ui.show()
    sys.exit(app.exec_())




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
        painter.begin(self)



                
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
        painter.end()

class ThreadNetworkRecv(QThread):
    signal_recv_data= pyqtSignal(list)
    def __init__(self,socket_net):
        super().__init__()
        self.__socket_net = socket_net
    def run(self):
        global communication_flag # true is recv status,false is send status
        while True:
            if communication_flag:
                data=self.__socket_net.recv(1024).decode()
                self.signal_recv_data.emit(string2list(data))# data: vector,velocity,angle,omega
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
        global communication_flag
        if not communication_flag:
            cal_f=self.__pids.calculate(self.__data)
            self.__socket_net.send(str(cal_f).encode("utf-8"))
            communication_flag=True
class Ui_Form(QtWidgets.QWidget):
    def __init__(self,rod,path,pids) -> None:
        super().__init__()
        self.setupUi(self,rod)
        self.__rod=rod
        self.__netRecv=ThreadNetworkRecv(path)
        self.__netSend=ThreadNetworkSend(path,pids)
        self.__netRecv.signal_recv_data.connect(self.receiveData)
        self.__netRecv.start()
        # self.__netSend.start()
    def setupUi(self, Form,rod):
        Form.setObjectName("Form")
        Form.resize(400, 257)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")

        self.rodWidget=RodWidget(rod)
        
        self.gridLayout.addWidget(self.rodWidget, 1, 0, 1, 1)
        self.gridLayout.setSpacing(1)
        self.setLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)



    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

    def receiveData(self,data):
        # self.rodWidget.
        #picture update
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
    path.connect(address)
    # init done
    pids=MultiPID(t,[21,0,0],[21,0,0],[21,0,0],[21,0,0])



    ui=Ui_Form(rod,path,pids)
    # print()
    ui.show()
    sys.exit(app.exec_())
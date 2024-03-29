import sys
from PyQt5 import QtWidgets

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5 import QtCore
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtCore import pyqtSignal,QThread,QTimer,QSize
import socket
from time import sleep
from RodClass import Rod

class MyCanvas(FigureCanvas):
    def __init__(self,parent=None,width=4,height=5,dpi=100):
        self.fig=Figure(figsize=(width, height),dpi=dpi)
        self.axes=self.fig.add_subplot(111)
        self.__conn=None
        # self.run()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
    # def run(self):
    #     pass
# class ThreadNetworkRecv(QThread):
#     signal_recv_data= pyqtSignal(list)
#     def __init__(self,socket_net):
#         super().__init__()
#         self.__socket_net = socket_net
#     def run(self):
#         global communication_flag # true is recv status,false is send status
        
#         if not communication_flag:
#             data=self.__socket_net.recv(1024).decode()
#             self.signal_recv_data.emit(string2list(data))# data: vector,velocity,angle,omega
#             communication_flag=False
# class ThreadNetworkSend(QThread):
#     def __init__(self,socket_net,rod):
#         super().__init__()
#         self.__socket_net = socket_net
#         self.__data = [0,0,0,0]
#     def setData(self,data):
#         self.__data = data
#     def run(self):
#         global communication_flag
#         while True:
#             if communication_flag:
#                 cal_f=self.__pids.calculate(self.__data)
#                 self.__socket_net.send(str(cal_f).encode("utf-8"))
#                 communication_flag=True
class ThreadNetwork(QThread):
    signal_connected=pyqtSignal()
    def __init__(self,socket_net,rod,f):
        super().__init__()
        self.communication_wait_flag=True
        self.__socket_net = socket_net
        self.__rod=rod
        # test part start
        # print(self.__rod)
        # test part end
        # self.__rodData=rodData
        self.__f=f
        # self.parent.rod.setAngle(5)
        pass
    def run(self):
        if(self.communication_wait_flag):
            self.__connect2client,self.__addr=self.__socket_net.accept()
            print("connection established: ",self.__addr)
            # self.parent.rod.setAngle(5)
            self.signal_connected.emit()
            self.communication_wait_flag=False
    
        while not self.communication_wait_flag:
            # data=self.__rodData[[0,1,3,4]]
            data=self.__rod.getSendData()
            # print("send data: ",data)
            try:
                self.__connect2client.send(str(data).encode("utf-8")) 
                recvData=self.__connect2client.recv(1024).decode()
            except WindowsError:
                pass
            if recvData.startswith("reset"):
                self.__rod.reset()
                # self.__rod.setAngle(5)
                # self.__rod.setV(0.5)
            else:
                try:
                    self.__f=float(recvData)
                except ValueError:
                    self.__f=0
                # test part start
                # print(self.__f)
                # test part end
                self.__rod.setF(self.__f)
            sleep(0.01)
            # print("recv f: ",self.__f)
# not used
class ThreadRod(QThread):
    signal_data_update=pyqtSignal(str,float)
    signal_data_update_all=pyqtSignal(list)
    def __init__(self,rod,parent):
        super().__init__()
        self.__rod=rod
        # test part start
        # print(self.__rod)
        # test part end
        # self.parent=parent
    def run(self):
        while True:
            # self.f=
            self.__rod.setF(self.parent.f)
            # self.parent.rodData=
            data=self.__rod.update()
            # print(data[3])
            self.signal_data_update_all.emit(data)
            # sleep(0.001)
            # sleep(0.1)


class MyWindow(QtWidgets.QWidget):
    signal_data_update=pyqtSignal(str,float)
    signal_data_update_all=pyqtSignal(list)
    # signal_net_connected=pyqtSignal(object) 
    def __init__(self,rod,connection,t):
        QtWidgets.QWidget.__init__(self)

        self.rod=rod
        # test part start
        # print(rod)
        # print(self.rod)
        # test part end
        
        self.saveCount=4000
        self.maxSaveCount=40000
        self.f=0 # 隐式使用
        self.rodData=[0,0,0,0,0,0] # 隐式使用
        

        # self.__connection=
        # self.__rodUpdate=ThreadRod(rod,parent=self)
        self.__rodUpdataT=QTimer(self)
        self.__network=ThreadNetwork(connection,self.rod,self.f)

        self.vector=[]
        self.velocity=[]
        self.angle=[]
        self.omega=[]
        self.vectorMax=0
        self.velocityMax=0
        self.angleMax=0
        self.omegaMax=0

        self.__rodUpdataT.timeout.connect(self.updateRod)
        self.signal_data_update.connect(self.update_data)
        self.signal_data_update_all.connect(self.update_data_all)
        self.__network.signal_connected.connect(self.networdConnected)
        # self.__rodUpdate.signal_data_update.connect(self.update_data)
        # self.__rodUpdate.signal_data_update_all.connect(self.update_data_all)
        # self.signal_net_connected.connect(self.connected_net)

        # self.__rodUpdate.start()
        self.__rodUpdataT.start(int(t*1000))
        self.__network.start()


        
        # todo: 增加模型变量修改，及确认键
        # todo: 干扰量加入。

        self.resize(575,860)

        vbox=QtWidgets.QVBoxLayout()

        hbox1=QtWidgets.QHBoxLayout()
        self.label_vector=QtWidgets.QLabel("vector",self)
        self.canvas_vector=MyCanvas(self,width=15,height=15,dpi=100)
        self.canvas_vector.setMinimumSize(QSize(512, 205))
        hbox1.addWidget(self.label_vector)
        hbox1.addWidget(self.canvas_vector)
        hbox1.addStretch()

        hbox2=QtWidgets.QHBoxLayout()
        self.label_velocity=QtWidgets.QLabel("velocity",self)
        self.canvas_velocity=MyCanvas(self,width=15,height=15,dpi=100)
        self.canvas_velocity.setMinimumSize(QSize(512, 205))
        hbox2.addWidget(self.label_velocity)
        hbox2.addWidget(self.canvas_velocity)
        hbox2.addStretch()

        hbox3=QtWidgets.QHBoxLayout()
        self.label_angle=QtWidgets.QLabel("angle",self)
        self.canvas_angle=MyCanvas(self,width=15,height=15,dpi=100)
        self.canvas_angle.setMinimumSize(QSize(512, 205))
        hbox3.addWidget(self.label_angle)
        hbox3.addWidget(self.canvas_angle)
        hbox3.addStretch()

        hbox4=QtWidgets.QHBoxLayout()
        self.label_omega=QtWidgets.QLabel("omega",self)
        self.canvas_omega=MyCanvas(self,width=15,height=15,dpi=100)
        self.canvas_omega.setMinimumSize(QSize(512, 205))
        hbox4.addWidget(self.label_omega)
        hbox4.addWidget(self.canvas_omega)
        hbox4.addStretch()



        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addStretch(2)
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.rodMassEdit = QtWidgets.QLineEdit(self)
        self.rodMassEdit.setObjectName("rodMassEdit")
        self.gridLayout_2.addWidget(self.rodMassEdit, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.rodLengthEdit = QtWidgets.QLineEdit(self)
        self.rodLengthEdit.setObjectName("rodLengthEdit")
        self.gridLayout_2.addWidget(self.rodLengthEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.carMassEdit = QtWidgets.QLineEdit(self)
        self.carMassEdit.setObjectName("carMassEdit")
        self.gridLayout_2.addWidget(self.carMassEdit, 2, 1, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_2)
        self.modelButton = QtWidgets.QPushButton(self)
        self.modelButton.setObjectName("modelButton")
        self.horizontalLayout_2.addWidget(self.modelButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.vectorDisturbEdit = QtWidgets.QLineEdit(self)
        self.vectorDisturbEdit.setObjectName("vectorDisturbEdit")
        self.gridLayout.addWidget(self.vectorDisturbEdit, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.velocityDisturbEdit = QtWidgets.QLineEdit(self)
        self.velocityDisturbEdit.setObjectName("velocityDisturbEdit")
        self.gridLayout.addWidget(self.velocityDisturbEdit, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.angleDisturbEdit = QtWidgets.QLineEdit(self)
        self.angleDisturbEdit.setObjectName("angleDisturbEdit")
        self.gridLayout.addWidget(self.angleDisturbEdit, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.omegaDisturbEdit = QtWidgets.QLineEdit(self)
        self.omegaDisturbEdit.setObjectName("omegaDisturbEdit")
        self.gridLayout.addWidget(self.omegaDisturbEdit, 3, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.disturbButton = QtWidgets.QPushButton(self)
        self.disturbButton.setObjectName("disturbButton")
        self.horizontalLayout.addWidget(self.disturbButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        hbox=QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(self.verticalLayout_2)

        self.setLayout(hbox)

        self.label.setText("杆质量")
        self.label_2.setText("杆长度")
        self.label_3.setText("车质量")
        self.modelButton.setText("模型设置")
        self.label_4.setText("位移扰动")
        self.label_5.setText("速度扰动")
        self.label_6.setText("角度扰动")
        self.label_7.setText("角速度扰动")
        self.disturbButton.setText("扰动设置")

        self.rodLengthEdit.setText("1")
        self.rodMassEdit.setText("5")
        self.carMassEdit.setText("5000")

        # 扰动ui显示设置
        self.vectorDisturbEdit.setText("0")
        self.velocityDisturbEdit.setText("0")
        self.angleDisturbEdit.setText("0")
        self.omegaDisturbEdit.setText("0")


        # ui connect
        self.modelButton.clicked.connect(self.setModel)
        self.disturbButton.clicked.connect(self.addDisturb)


        self.x = [i for i in range(self.saveCount)]                                     #画图
        # self.p = 0.0
        self.y = [0]*self.saveCount
        # print(len(self.y))

        self.canvas_angle.axes.set_ylim((-90,90))
        self.canvas_omega.axes.set_ylim((-15,15))
        self.canvas_vector.axes.set_ylim((-150,150))
        self.canvas_velocity.axes.set_ylim((-15,15))
        # self.canvas_velocity.axes.set_yli


        self.line_vector,=self.canvas_vector.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_velocity,=self.canvas_velocity.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_angle,=self.canvas_angle.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_omega,=self.canvas_omega.axes.plot(self.x,self.y,animated=True,lw=2)

        self.ani_vector=FuncAnimation(self.canvas_vector.figure,
                                      self.update_line_vector,blit=True,interval=10,save_count=3000)
        self.ani_velocity=FuncAnimation(self.canvas_velocity.figure,
                                      self.update_line_velocity,blit=True,interval=10,save_count=3000)
        self.ani_angle=FuncAnimation(self.canvas_angle.figure,
                                      self.update_line_angle,blit=True,interval=10,save_count=3000)
        self.ani_omega=FuncAnimation(self.canvas_omega.figure,
                                      self.update_line_omega,blit=True,interval=10,save_count=3000)
    
    # def connected_net(self,conn):
    #     self.__conn=conn


    def update_line_vector(self,i):
        # self.saveCount 是 self.x 的长度
        self.vector.append(self.rodData[0])
        # self.vectorMax=max(self.vectorMax,self.rodData[0])
        # self.
        if(len(self.vector)<self.saveCount):
            vector=np.pad(self.vector,((self.saveCount-len(self.vector),0)),"constant",constant_values=0)
        else:
            vector=self.vector[-self.saveCount:]
            # print(set(vector))
        # self.y = np.sin(self.x + 0)
        
        self.line_vector.set_ydata(vector)
        
        return [self.line_vector]
    def update_line_velocity(self,i):
        self.velocity.append(self.rodData[1])
        if(len(self.velocity)<self.saveCount):
            velocity=np.pad(self.velocity,((self.saveCount-len(self.velocity),0)),"constant",constant_values=0)
        else:
            velocity=self.velocity[-self.saveCount:]
        self.line_velocity.set_ydata(velocity)
        return [self.line_velocity]
    def update_line_angle(self,i):
        self.angle.append(self.rodData[3])
        if(len(self.angle)<self.saveCount):
            angle=np.pad(self.angle,((self.saveCount-len(self.angle),0)),"constant",constant_values=0)
        else:
            angle=self.angle[-self.saveCount:]
        self.line_angle.set_ydata(angle)
        return [self.line_angle]
    def update_line_omega(self,i):
        self.omega.append(self.rodData[4])
        if(len(self.omega)<self.saveCount):
            omega=np.pad(self.omega,((self.saveCount-len(self.omega),0)),"constant",constant_values=0)
        else:
            omega=self.omega[-self.saveCount:]
        self.line_omega.set_ydata(omega)
        return [self.line_omega]

    def update_data(self,type,data):
        if(type=="vector"):
            self.update_line_vector(data)
        elif(type=="velocity"):
            self.update_line_velocity(data)
        elif(type=="angle"):
            self.update_line_angle(data)
        elif(type=="omega"):
            self.update_line_omega(data)
        else:
            pass
            
    def update_data_all(self,rodData):
        self.rodData =rodData
        # l=rodData[[0,1,3,4]]
        if len(self.vector)>=self.maxSaveCount:
            self.vector=self.vector[-self.saveCount:]
            self.velocity=self.velocity[-self.saveCount:]
            self.angle=self.angle[-self.saveCount:]
            self.omega=self.omega[-self.saveCount:]
        # self.update_line_vector(rodData[0])
        # self.update_line_velocity(rodData[1])
        # self.update_line_angle(rodData[3])
        # self.update_line_omega(rodData[4])
        # self.update_line_vector(0)
        # self.update_line_velocity(0)
        # self.update_line_angle(0)
        # self.update_line_omega(0)
    def updateRod(self):
        # self.f=
        # print(self.f)
        # self.rod.setF(self.f)
        # print(self.rod.getF())
        # self.parent.rodData=
        data=self.rod.update()
        # test part start
        # print("calculate data: ",data)
        # test part end
        self.signal_data_update_all.emit(data)
        # sleep(0.001)
    def networdConnected(self):
        self.rod.setAngle(5)
        self.rod.setV(0.5)
        # pass
    
    def setModel(self):
        self.rod.setm(float(self.rodMassEdit.text()))
        self.rod.setM(float(self.carMassEdit.text()))
        self.rod.setL(float(self.rodLengthEdit.text()))
    def addDisturb(self):
        self.rod.addVectorDisturb(float(self.vectorDisturbEdit.text()))
        self.rod.addVelocityDisturb(float(self.velocityDisturbEdit.text()))
        self.rod.addAngleDisturb(float(self.angleDisturbEdit.text()))
        self.rod.addOmegaDisturb(float(self.omegaDisturbEdit.text()))
        

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
    # communication_flag=True
    qApp = QtWidgets.QApplication(sys.argv)
    t=0.005
    rod=Rod(5,1,t)

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address="localhost"
    port=12345
    s.bind((address, port))
    s.listen(1)

    # conn,addr=s.accept()



    aw = MyWindow(rod,s,t)
    aw.show()
    sys.exit(qApp.exec_())
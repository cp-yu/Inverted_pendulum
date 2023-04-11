import sys
from PyQt5 import QtWidgets

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtCore import pyqtSignal

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
class MyWindow(QtWidgets.QWidget):
    signal_data_update=pyqtSignal(str,float)
    signal_data_update_all=pyqtSignal(list)
    # signal_net_connected=pyqtSignal(object)
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        # self.resize(600,600)
        vbox=QtWidgets.QVBoxLayout()
        self.signal_data_update.connect(self.update_data)
        self.signal_data_update_all.connect(self.update_data_all)
        # self.signal_net_connected.connect(self.connected_net)
        

        hbox1=QtWidgets.QHBoxLayout()
        self.label_vector=QtWidgets.QLabel("vector",self)
        self.canvas_vector=MyCanvas(self,width=15,height=15,dpi=100)
        hbox1.addWidget(self.label_vector)
        hbox1.addWidget(self.canvas_vector)
        hbox1.addStretch()

        hbox2=QtWidgets.QHBoxLayout()
        self.label_velocity=QtWidgets.QLabel("velocity",self)
        self.canvas_velocity=MyCanvas(self,width=15,height=15,dpi=100)
        hbox2.addWidget(self.label_velocity)
        hbox2.addWidget(self.canvas_velocity)
        hbox2.addStretch()

        hbox3=QtWidgets.QHBoxLayout()
        self.label_angle=QtWidgets.QLabel("angle",self)
        self.canvas_angle=MyCanvas(self,width=15,height=15,dpi=100)
        hbox3.addWidget(self.label_angle)
        hbox3.addWidget(self.canvas_angle)
        hbox3.addStretch()

        hbox4=QtWidgets.QHBoxLayout()
        self.label_omega=QtWidgets.QLabel("omega",self)
        self.canvas_omega=MyCanvas(self,width=15,height=15,dpi=100)
        hbox4.addWidget(self.label_omega)
        hbox4.addWidget(self.canvas_omega)
        hbox4.addStretch()



        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addStretch(2)
        self.setLayout(vbox)


        self.x = np.linspace(0, 5*np.pi, 400)                                     #画图
        self.p = 0.0
        self.y = np.sin(self.x + self.p)
        # print(len(self.y))

        self.line_vector,=self.canvas_vector.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_velocity,=self.canvas_velocity.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_angle,=self.canvas_angle.axes.plot(self.x,self.y,animated=True,lw=2)
        self.line_omega,=self.canvas_omega.axes.plot(self.x,self.y,animated=True,lw=2)

        self.ani_vector=FuncAnimation(self.canvas_vector.figure,
                                      self.update_line_vector,blit=True,interval=25)
        self.ani_velocity=FuncAnimation(self.canvas_velocity.figure,
                                      self.update_line_velocity,blit=True,interval=25*2)
        self.ani_angle=FuncAnimation(self.canvas_angle.figure,
                                      self.update_line_angle,blit=True,interval=25*3)
        self.ani_omega=FuncAnimation(self.canvas_omega.figure,
                                      self.update_line_omega,blit=True,interval=25*4)
    
    # def connected_net(self,conn):
    #     self.__conn=conn


    def update_line_vector(self,i):
        # 400 是 self.x 的长度
        self.vector=self.y[100:] # 测试语句
        if(len(self.vector)<400):
            vector=np.pad(self.vector,((400-len(self.vector),0)),"constant",constant_values=0)
        # self.y = np.sin(self.x + 0)
        
        self.line_vector.set_ydata(vector)
        
        return [self.line_vector]
    def update_line_velocity(self,i):
        self.p+=0.02
        self.y = np.cos(self.x + self.p)
        self.line_velocity.set_ydata(self.y)
        return [self.line_velocity]
    def update_line_angle(self,i):
        self.p+=0.03
        self.y = np.sin(self.x + self.p+90)
        self.line_angle.set_ydata(self.y)
        return [self.line_angle]
    def update_line_omega(self,i):
        self.p+=0.04
        self.y = np.cos(self.x + self.p+45)
        self.line_omega.set_ydata(self.y)
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
            
    def update_data_all(self,l):
        self.update_line_vector("vector",l[0])
        self.update_line_velocity("velocity",l[1])
        self.update_line_angle("angle",l[2])
        self.update_line_omega("omega",l[3])

if __name__ == "__main__":

    qApp = QtWidgets.QApplication(sys.argv)
    aw = MyWindow()
    aw.show()
    sys.exit(qApp.exec_())
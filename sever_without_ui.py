import threading
# from sever_display import  MyWindow
from RodClass import Rod
import socket
import sys
# from PyQt5 import QtWidgets
# from PyQt5.QtCore import pyqtSignal
# import time

class RodThread(threading.Thread):
    def __init__(self,rod,ui,net,name=None):
        super(RodThread,self).__init__()
        self.__rod=rod
        # self.__ui=ui
        self.__net=net
        self.__f=0
    def run(self):
        while True:
            self.__rod.setF(self.__f)
            self.__rod.update()
            data=self.__rod.getData()
            print(data)
            # signal.emit()
            # self.__ui.signal_data_update("vector",self.__rod.getX())
            # self.__ui.signal_data_update("velocity",self.__rod.getV())
            # self.__ui.signal_data_update("angle",self.__rod.getAngle())
            # self.__ui.signal_data_update("omega",self.__rod.getOmega())

            # self.__ui.signal_data_update_all.emit(data)

            # todo: net communication(third thread)
            #   self.__net.send(balabala)
            #   recv_data=self.__net.recv()
            #   self.__f=process(recv_data)
            if self.__net.isConnected():
                self.__net.send(data)
                self.__f=float(self.__net.recv())
            # todo: sleep(25)

class Connection():
    def __init__(self):
        self.connect2client=None
    def isConnected(self):
        return self.connect2client is not None
    def send(self,data):
        self.connect2client.send(str(data))
    def recv(self):
        return self.connect2client.recv(1024)

# def fun_ui():
#     # qApp = QtWidgets.QApplication(sys.argv)
#     # aw = MyWindow()
#     ui.show()
#     sys.exit(qApp.exec_())
def fun_wait_connnection():
    c,addr = socket2client.accept()
    print("链接地址:",addr)
    connection.connect2client=c
#  replace by Connection.fun
# def fun_communication():
#     pass

def string2list(s):
    res=s.strip('[')
    res=res.strip(']')
    res=res.replace(" ","")
    res=res.split(',')
    res=[float(i) for i in res]
    return res

if __name__ == '__main__':
    # qApp = QtWidgets.QApplication(sys.argv)
    # ui = MyWindow()
    rod=Rod(1,1,0.0001)    
    # todo: socket 实例化
    socket2client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host=socket.gethostname()
    # try:
    #     port=12345
    #     socket2client.bind((host,port))
    # except socket.error:
    #     port+=1
    #     socket2client.bind((host,port))
    port=12345
    socket2client.bind((host,port))
    socket2client.listen(1)
    # socket 实例完成
    connection=Connection()
    # thread_ui=threading.Thread(target=fun_ui)
    thread_net=threading.Thread(target=fun_wait_connnection)
    RT=RodThread(rod,None,connection)


    # thread_ui.start()
    # RT.start()
    thread_net.start()

    # connection.connect2client.close()

    # RT.join()

    # sys.exit(qApp.exec_())
# PID类，主要用于处理pid计算
class PID:
    def __init__(self,p,i,d,t):
        self.__KP = p
        self.__KI = i
        self.__KD = d

        self.__enabled = True  #是否使能此级闭环

        self.__ref = 0.0        #调节量的期望值（初始偏差）,初始化OFFSET
        self.__fdb = 0.0        #调节量的反馈值（调节后的偏差） ，初始化0 
        self.__Ek = 0.0         #当前的偏差
        self.__Sk = 0.0         #历史偏差（积分） 
        self.__Dk = 0.0         #最近两次偏差值之差 
        self.__Ek_1 = 0.0       #上次偏差
        self.__Ek_2 = 0.0       #本次偏差 
        self.__out = 0.0        #输出控制量 
        self.__outMax = 100.0   #最大100 
        self.__outMin = 100.0   #最小-100 
        self.__T = t            #采样周期（单片机系统中这个值应该用单片机定时器测，每轮计算时更新）

    def isEnable(self):
        return self.__enabled

    def setEnable(self,flag):
        self.__enabled = flag

    def setRef(self,ref):
        self.__ref = ref
    
    def setFdb(self,fdb):
        self.__fdb = fdb
    
    def setKP(self,kp):
        self.__KP = kp
    def getKP(self):
        return self.__KP

    def setKI(self,ki):
        self.__KI = ki
    def getKI(self):
        return self.__KI

    def setKD(self,kd):
        self.__KD = kd
    def getKD(self):
        return self.__KD

    def setT(self,t):
        self.__T = t
    def getT(self):
        return self.__T

    def getPIDPara(self):
        para = [self.__enabled,self.__KP,self.__KI,self.__KD]
        return para
    
    def setPIDPara(self,para):
        #print(para)
        if para[0] == 'True':
            self.setEnable(True)
        else:
            self.setEnable(False)
        
        for i in range(3):
            if para[i] == '': 
                para[i] = 0.0

        self.setKP(float(para[1]))
        self.setKI(float(para[2]))
        self.setKD(float(para[3]))

    def clear(self):
        self.__ref = 0.0        #调节量的期望值（初始偏差）,初始化OFFSET
        self.__fdb = 0.0        #调节量的反馈值（调节后的偏差） ，初始化0 
        self.__Ek = 0.0         #当前的偏差
        self.__Sk = 0.0         #历史偏差（积分） 
        self.__Dk = 0.0         #最近两次偏差值之差 
        self.__Ek_1 = 0.0       #上次偏差
        self.__Ek_2 = 0.0       #本次偏差 
        self.__out = 0.0        #输出控制量 

    def calculate(self):
        self.__Ek = self.__ref - self.__fdb
        self.__Sk += self.__Ek * self.__T
        
        self.__out = 1.0 * (self.__KP * self.__Ek + self.__KI * self.__Sk + self.__KD * self.__Dk)
#        if self.__out > self.__outMax:
#            self.__out = self.__outMax
#        if self.__out < self.__outMin:
#            self.__out = self.__outMin

        self.__Ek_1 = self.__Ek_2
        self.__Ek_2 = self.__Ek

        self.__Dk = (self.__Ek_2 - self.__Ek_1)/self.__T
        return self.__out

class MultiPID:
    def __init__(self,t,varAPos=[0,0,0],varASpd=[0,0,0],varDPos=[0,0,0],varDSpd=[0,0,0]):
        self.PID_angPos = PID(varAPos[0],varAPos[1],varAPos[2],t)                   #PID计算对象
        self.PID_angSpd = PID(varASpd[0],varASpd[1],varASpd[2],t)
        self.PID_dispPos = PID(varDPos[0],varDPos[1],varDPos[2],t)
        self.PID_dispSpd = PID(varDSpd[0],varDSpd[1],varDSpd[2],t)

        self.ref_disp=0
        self.ref_ang=0

        # controller = {'AngPos':PID_angPos , 'AngSpd':PID_angSpd , 'DispPos':PID_dispPos , 'DispSpd':PID_dispSpd}

        self.res = [0.0,0.0,0.0,0.0]     #四个环的输出
        self.angOut = 0.0                #摆角两个环综合输出
        self.dispOut = 0.0               #位移两个环综合输出
        
    def calculate(self,rod): #rod is list of four float: vector, velocity, angle, omega
        #位移位置环
        if self.PID_dispPos.isEnable():
            self.PID_dispPos.setRef(self.ref_disp)      #位置期望在原点，注意要放在原点附近才行
            self.PID_dispPos.setFdb(rod[0])
            self.res[2] = self.PID_dispPos.calculate()

        self.dispOut = self.res[2]

        #位移速度环
        if self.PID_dispSpd.isEnable():

            self.PID_dispSpd.setRef(self.res[2])  
            self.PID_dispSpd.setFdb(rod[1])
            self.res[3] = self.PID_dispSpd.calculate()

            self.dispOut = self.res[3]

        #摆角位置环
        if self.PID_angPos.isEnable():
            self.PID_angPos.setRef(self.ref_ang)   
            currentAng = rod[2]
            
            currentAng %= 360
            if currentAng > 180:
                currentAng -= 360
            self.PID_angPos.setFdb(currentAng)
            self.res[0] = self.PID_angPos.calculate()
        
        self.angOut = self.res[0]

        #摆角速度环
        if self.PID_angSpd.isEnable():

            self.PID_angSpd.setRef(self.res[0])  
            self.PID_angSpd.setFdb(rod[3])
            self.res[1] = self.PID_angSpd.calculate()

            self.angOut = self.res[1]
        
        # self.PIDCalSignal.emit(self.res)
        return self.angOut + self.dispOut

import tkinter as tk
import random
import math
import numpy as np
import sys
import time
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

class Counter:
    def __init__(self):
        self.dirtCollected = 0

    def itemCollected(self,canvas):
        self.dirtCollected += 1
        canvas.delete("dirtCount")
        canvas.create_text(50,50,anchor="w",\
                           text="Dirt collected: "+str(self.dirtCollected),\
                           tags="dirtCount")
        
    def getDirtCollected(self):
        return self.dirtCollected
    
class ListOfPositionsInMap:
    def __init__(self):
        self.list = []

class ListOfPositionsInMapPrior:
    def __init__(self):
        self.list = {}
        self.count = 0

class WaitingForBot:
    def __init__(self):
        self.list = {}

listOfPositions = ListOfPositionsInMap()
listOfPositionsPrior = ListOfPositionsInMapPrior()    
waitingTime = WaitingForBot()    

class Bot:

    def __init__(self,namep,canvasp):
        self.x = random.randint(100,900)
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.name = namep
        self.ll = 60 #axle width
        self.vl = 0.0
        self.vr = 0.0
        self.battery = 1000
        self.turning = 0
        self.moving = random.randrange(50,100)
        self.currentlyTurning = False
        self.map = np.zeros( (10,10) )
        self.canvas = canvasp
        self.currentPosition = 0
        self.countdown = None
        self.whereCurrentAndInListOfPositions = []
        self.whereIveBeen = []
        self.count = 0
        self.time = 0

    def brain(self,chargerL,chargerR):
        # wandering behaviour
        #print(type(self.whereCurrentAndInListOfPositions))
        pass

    def thinkAndAct(self, count):
        completed = False
        if self.time==1000:
            print("complete: total dirt collected "+str(count))
            completed = True
        
        self.time += 1

        if completed:
            return count
        else:
            return None
        
        
        
        
    def draw(self,canvas):
        points = [ (self.x + 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) - 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) - 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x - 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y + 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                   (self.x + 30*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                   (self.y - 30*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                ]
        canvas.create_polygon(points, fill="blue", tags=self.name)

        self.sensorPositions = [ (self.x + 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y - 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta), \
                                 (self.x - 20*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y + 20*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta)  \
                            ]
    
        centre1PosX = self.x 
        centre1PosY = self.y
        canvas.create_oval(centre1PosX-15,centre1PosY-15,\
                           centre1PosX+15,centre1PosY+15,\
                           fill="gold",tags=self.name)
        canvas.create_text(self.x,self.y,text=str(self.battery),tags=self.name)

        wheel1PosX = self.x - 30*math.sin(self.theta)
        wheel1PosY = self.y + 30*math.cos(self.theta)
        canvas.create_oval(wheel1PosX-3,wheel1PosY-3,\
                                         wheel1PosX+3,wheel1PosY+3,\
                                         fill="red",tags=self.name)

        wheel2PosX = self.x + 30*math.sin(self.theta)
        wheel2PosY = self.y - 30*math.cos(self.theta)
        canvas.create_oval(wheel2PosX-3,wheel2PosY-3,\
                                         wheel2PosX+3,wheel2PosY+3,\
                                         fill="green",tags=self.name)

        sensor1PosX = self.sensorPositions[0]
        sensor1PosY = self.sensorPositions[1]
        sensor2PosX = self.sensorPositions[2]
        sensor2PosY = self.sensorPositions[3]
        canvas.create_oval(sensor1PosX-3,sensor1PosY-3, \
                           sensor1PosX+3,sensor1PosY+3, \
                           fill="yellow",tags=self.name)
        canvas.create_oval(sensor2PosX-3,sensor2PosY-3, \
                           sensor2PosX+3,sensor2PosY+3, \
                           fill="yellow",tags=self.name)
        
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,registryPassives,dt):
        if self.battery>0:
            self.battery -= 1
        if self.battery==0:
            self.vl = 0
            self.vr = 0
                
        if self.vl==self.vr:
            R = 0
        else:
            R = (self.ll/2.0)*((self.vr+self.vl)/(self.vl-self.vr))
        omega = (self.vl-self.vr)/self.ll
        ICCx = self.x-R*math.sin(self.theta) #instantaneous centre of curvature
        ICCy = self.y+R*math.cos(self.theta)
        m = np.matrix( [ [math.cos(omega*dt), -math.sin(omega*dt), 0], \
                        [math.sin(omega*dt), math.cos(omega*dt), 0],  \
                        [0,0,1] ] )
        v1 = np.matrix([[self.x-ICCx],[self.y-ICCy],[self.theta]])
        v2 = np.matrix([[ICCx],[ICCy],[omega*dt]])
        newv = np.add(np.dot(m,v1),v2)
        newX = newv.item(0)
        newY = newv.item(1)
        newTheta = newv.item(2)
        newTheta = newTheta%(2.0*math.pi) #make sure angle doesn't go outside [0.0,2*pi)
        self.x = newX
        self.y = newY
        self.theta = newTheta        
        if self.vl==self.vr: # straight line movement
            self.x += self.vr*math.cos(self.theta) #vr wlog
            self.y += self.vr*math.sin(self.theta)
        if self.x<0.0:
            self.x=999.0
        if self.x>1000.0:
            self.x = 0.0
        if self.y<0.0:
            self.y=999.0
        if self.y>1000.0:
            self.y = 0.0
        self.updateMap()
        canvas.delete(self.name)
        self.draw(canvas)

    def updateMap(self):
        xMapPosition = int(math.floor(self.x/100))
        yMapPosition = int(math.floor(self.y/100))
        self.map[xMapPosition][yMapPosition] = 1
        self.currentPosition = (xMapPosition, yMapPosition)
        self.drawMap()
        self.whereIveBeen.append((xMapPosition, yMapPosition))
        #print(self.whereIveBeen)
        #print(listOfPositions.list)
        #print(self.currentPosition)
        print(self.currentPosition)

        #if a new place
        if (xMapPosition, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition) not in listOfPositionsPrior.list: 
            listOfPositionsPrior.list[(xMapPosition, yMapPosition)] = (1)
            
        #if time has come for it to go into actual list
        elif (xMapPosition, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition) in listOfPositionsPrior.list and listOfPositionsPrior.list[(xMapPosition, yMapPosition)] == 0:
            listOfPositions.list.append((xMapPosition, yMapPosition))
            listOfPositionsPrior.list.pop((xMapPosition, yMapPosition))
            
        #takes off countdown when before 0
        elif (xMapPosition, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition) in listOfPositionsPrior.list:
            listOfPositionsPrior.list[(xMapPosition, yMapPosition)] -= 1
        
            
            #print("h")
            #print(self.count)
            #print(self.currentPosition)

        
        
        #RIGHT, BELOW AND ABOVE FILLED IN
        if len(self.whereIveBeen) > 50 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list:
            
            #FROM BELOW + LEFT FREE
                
            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from below + turning left 1 with only left free")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from below + left 2")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 3")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 4")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 5")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 6")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 7")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 8")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 28")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 38")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 48")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0

            #FROM ABOVE + LEFT FREE
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from above turning right with only left free")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                print(47)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(46)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(45)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(44)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(43)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(42)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(41)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(40)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(39)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(38)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(37)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(36)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(35)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(34)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(33)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(32)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(31)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(30)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(29)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(28)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(27)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(26)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(25)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(24)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(23)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(22)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(21)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(20)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(19)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(18)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(17)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(16)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(15)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(14)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(13)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(12)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(11)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(10)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(9)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(8)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(7)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(6)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(5)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(4)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(3)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(2)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(1)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                #print(self.whereCurrentAndInListOfPositions)
                print("done")
                
                self.vl = 2.0
                self.vr = 0.0
                self.vl = 2.0
                self.vr = 2.0
            
            
            
            
        
        #if the surrounding places on the map are all within the list that have been explored
        
        #LEFT, BELOW AND ABOVE FILLED IN, RIGHT FREE
        elif len(self.whereIveBeen) > 50 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list:
            
            
            
            #FROM BELOW + GOING RIGHT
            if self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from below going right as right is only free")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 2")
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 3")
                #print(16)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 4")
                #print(15)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 5")
                #print(14)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 6")
                #print(13)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 7")
                #print(12)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 8")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 9")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 10")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 11")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 12")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 13")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 14")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 15")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 16")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 17")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 18")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 19")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 20")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 21")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 22")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 23")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 24")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 25")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 26")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 27")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 28")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 29")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 30")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 31")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 32")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 33")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 34")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 35")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 36")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 37")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 38")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 39")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 40")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 41")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 42")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 43")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 44")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 45")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 46")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 47")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below going right 48")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
               # print(self.whereCurrentAndInListOfPositions)
                print("done")
                
                self.vl = 2.0
                self.vr = 0.0
                self.vl = 2.0
                self.vr = 2.0

            #FROM ABOVE + GOING TO RIGHT OF SCREEN
            elif self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count = 0
                
                
                print("from above + turning left (right of screen) 1 with right only free")
                #print(self.currentPosition)
                #print(self.whereIveBeen[-1])
               # print(self.whereIveBeen[-2])
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 2")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 3")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 4")
                
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 5")
                
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 6")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 7")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 8")

                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 28")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 38")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 48")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from above + right 49")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0
            
            '''elif self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                
                print("from above + right 1")
                #print(self.currentPosition)
                #print(self.whereIveBeen[-1])
                #print(self.whereIveBeen[-2])
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 2")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 3")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 4")
                
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 5")
                
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 6")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 7")
                
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 8")

                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 28")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 38")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 48")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from above + right 49")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0'''

        #ABOVE + BELOW CURRENT POSITION FILLED
        
        elif len(self.whereIveBeen) > 50 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list:

            #TURNING LEFT

            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from below + turning left 1 with left + right free")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from below + left 2")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 3")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 4")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 5")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 6")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 7")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 8")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 28")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 38")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 48")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0

            #FROM ABOVE + LEFT FREE
            #TURNING RIGHT
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from above going right with left and right free")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                print(47)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(46)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(45)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(44)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(43)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(42)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(41)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(40)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(39)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(38)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(37)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(36)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(35)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(34)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(33)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(32)
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(31)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(30)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(29)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(28)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(27)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(26)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(25)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(24)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(23)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(22)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(21)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(20)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(19)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(18)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(17)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(16)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(15)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(14)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(13)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(12)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(11)
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(10)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(9)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(8)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(7)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(6)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(5)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(4)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(3)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(2)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(1)
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                #print(self.whereCurrentAndInListOfPositions)
                print("done")
                
                self.vl = 2.0
                self.vr = 0.0
                self.vl = 2.0
                self.vr = 2.0

        #ABOVE ONLY FREE
        elif len(self.whereIveBeen) > 30 and (xMapPosition, yMapPosition-1) not in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list:

            #COMING FROM LEFT + TURNING LEFT
            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition-1, yMapPosition) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from left + turning left 1 with above only free")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from left + left 2")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 3")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 4")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 5")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 6")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 7")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 8")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 28")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 38")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + left 48")
                
                self.vl = 0.0
                self.vr = 2.0
            
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0

            #COMING FROM RIGHT AND TURNING RIGHT TO GO UP
            
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition+1, yMapPosition) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from right + turning right 1 with above only free")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 2")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 3")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 3")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 4")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 5")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 6")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 7")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 8")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 9")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 10")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 11")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 12")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 13")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 14")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 15")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 16")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 17")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 18")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 19")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 20")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 21")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 22")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 23")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 24")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 25")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 26")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 27")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 28")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 29")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 30")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 31")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 32")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 33")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 34")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 35")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 36")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 37")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 38")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 39")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 40")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 41")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 42")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 43")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 44")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 45")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 46")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + right 47")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from right + right 48")
                
                self.vl = 2.0
                self.vr = 0.0
                self.vl = 2.0
                self.vr = 2.0
                
        #BELOW ONLY FREE
        elif len(self.whereIveBeen) > 50 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition, yMapPosition+1) not in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list:

            #COMING FROM RIGHT + TURNING LEFT
            
            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition+1, yMapPosition) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from right + turning left 1 with below only free")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from right + left 2")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 3")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 4")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 5")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 6")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 7")
                
                self.vl = 0.0
                self.vr = 2.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 8")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 9")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 10")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 11")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 12")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 13")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 14")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 15")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 16")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 17")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 18")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 19")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 20")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 21")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 22")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 23")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 24")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 25")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 26")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 27")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 28")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 29")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 30")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 31")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 32")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 33")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 34")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 35")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 36")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 37")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 38")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 39")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 40")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 41")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 42")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 43")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 44")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 45")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 46")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 47")
                
                self.vl = 0.0
                self.vr = 2.0
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from right + left 48")
                
                self.vl = 0.0
                self.vr = 2.0
            
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition+1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 2.0
                self.vl = 2.0
                self.vr = 2.0

            #COMING FROM LEFT AND TURNING RIGHT
            
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition-1, yMapPosition) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("coming from left + turning right 1 with below only free")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 2")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 3")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 4")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 5")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 6")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 7")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 8")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 9")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 10")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 11")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 12")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 13")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 14")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 15")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 16")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 17")
                
                self.vl = 2.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 18")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 19")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 20")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 21")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-23] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-23] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 22")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-24] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-24] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 23")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-25] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-25] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 24")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-26] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-26] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 25")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-27] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-27] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 26")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-28] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-28] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 27")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-29] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-29] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 28")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-30] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-30] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 29")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-31] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-31] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 30")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-32] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-32] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 31")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-33] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-33] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 32")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-34] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-34] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 33")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-35] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-35] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 34")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-36] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-36] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 35")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-37] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-37] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 36")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-38] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-38] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 37")
                
                self.vl = 2.0
                self.vr = 0.0

            elif self.whereIveBeen[-39] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-39] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 38")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-40] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-40] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 39")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-41] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-41] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 40")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-42] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-42] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 41")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-43] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-43] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 42")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-44] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-44] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 43")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-45] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-45] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 44")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-46] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-46] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 45")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-47] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-47] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 46")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-48] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-48] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 47")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-49] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-49] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from left + right 48")
                
                self.vl = 2.0
                self.vr = 0.0
            
            elif self.whereIveBeen[-50] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-50] == (xMapPosition-1, yMapPosition):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from left + right 49")
                
                self.vl = 2.0
                self.vr = 0.0
                self.vl = 2.0
                self.vr = 2.0
        

        else:
            self.vl = 2.0
            self.vr = 2.0
            print("bypassed!")
            
            
        
        
            

    def drawMap(self):
        for xx in range(0,10):
            for yy in range(0,10):
                #print(xx,",",yy,)
                if self.map[xx][yy]==1:
                    self.canvas.create_rectangle(100*xx,100*yy,100*xx+100,100*yy+100,fill="pink",width=0,tags="map")
        self.canvas.tag_lower("map")
                
        
    def senseCharger(self, registryActives):
        xMapPosition = int(math.floor(self.x/100))
        yMapPosition = int(math.floor(self.y/100))
        self.map[xMapPosition][yMapPosition] = 1
        lightL = 0.0
        lightR = 0.0
        if (xMapPosition, yMapPosition) in listOfPositions.list:
                lx,ly = int(xMapPosition*100), int(yMapPosition*100)
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                lightL += 200000/(distanceL*distanceL)
                lightR += 200000/(distanceR*distanceR)
        #print(lightL+lightR)
        return lightL, lightR
    
    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2) )

    def collectDirt(self, canvas, registryPassives, count):
        toDelete = []
        for idx,rr in enumerate(registryPassives):
            if isinstance(rr,Dirt):
                if self.distanceTo(rr)<30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)
        for ii in sorted(toDelete,reverse=True):
            del registryPassives[ii]
        return registryPassives


class Dirt:
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep

    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-1,self.centreY-1, \
                                  self.centreX+1,self.centreY+1, \
                                  fill="grey",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY


def buttonClicked(x,y,registryActives):
    for rr in registryActives:
        if isinstance(rr,Bot):
            rr.x = x
            rr.y = y

def initialise(window):
    window.resizable(False,False)
    canvas = tk.Canvas(window,width=1000,height=1000)
    canvas.pack()
    return canvas

def register(canvas, noOfBots, amountOfDirt):
    registryActives = []
    registryPassives = []
    #noOfBots = 1
    #noOfDirt = 300
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i),canvas)
        registryActives.append(bot)
        bot.draw(canvas)
    for i in range(0,amountOfDirt):
        dirt = Dirt("Dirt"+str(i))
        registryPassives.append(dirt)
        dirt.draw(canvas)
    count = Counter()
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,registryActives) )
    return registryActives, registryPassives, count

def moveIt(canvas,registryActives,registryPassives,count,moves, window):
    #moves += 1
    for rr in registryActives:
        returnedCount = rr.thinkAndAct(count)
        if returnedCount != None:
            window.destroy()
            return returnedCount
        chargerIntensityL, chargerIntensityR = rr.senseCharger(registryPassives)
        rr.brain(chargerIntensityL, chargerIntensityR)
        rr.move(canvas,registryPassives,1.0)
        registryPassives = rr.collectDirt(canvas,registryPassives, count)
        numberOfMoves = 1000
        #if moves>numberOfMoves:
            #print("total dirt collected in",numberOfMoves,"moves is",count.dirtCollected, (listOfPositions.list.sort))
            #sys.exit()
    canvas.after(50,moveIt,canvas,registryActives,registryPassives,count,moves, window)

def runMain2(botNo, dirtNo):
    window = tk.Tk()
    canvas = initialise(window)
    registryActives, registryPassives, count = register(canvas, noOfBots=botNo, amountOfDirt=dirtNo)
    moves = 0
    moveIt(canvas,registryActives,registryPassives, count, moves, window)
    window.mainloop()
    return count.getDirtCollected()

#print(runMain(1, 300))

def runMainMultiple2(noOfTimes, botNo, dirtNo):
    counterList = []
    for times in range(noOfTimes):
        counterList.append(runMain2(botNo, dirtNo))
    return counterList

#print(runMainMultiple(1, 1, 300))

def runExperimentsWithDifferentParameters2():
    resultsTable = {}
    for condition in [1]:
        dirtCollectedList = runMainMultiple2(1,condition, 300)
        resultsTable[condition] = dirtCollectedList
    print(resultsTable)
    results = pd.DataFrame(resultsTable)
    print(results)
    results.to_excel("roboticsExperiment.xlsx")
    #print(ttest_ind(results[1],results[2]))
    print(results.mean(axis=1))
    results.boxplot(grid=True)
    plt.show()

print(runExperimentsWithDifferentParameters2())
import tkinter as tk
import random
import math
import numpy as np
import sys
import time

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

    def brain(self,chargerL,chargerR):
        # wandering behaviour
        #print(type(self.whereCurrentAndInListOfPositions))
        pass
        
        
        
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
        print(self.whereCurrentAndInListOfPositions)

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

        
        
        #RIGHT AND ABOVE FILLED IN
        if len(self.whereIveBeen) > 20 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list:
            
            #FROM BELOW + LEFT FREE
                
            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from below + left 1")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from below + left 2")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 3")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 4")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 5")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 6")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 7")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 8")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 9")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 10")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 11")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 12")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 13")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 14")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 15")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 16")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 5.0
                self.vl = 5.0
                self.vr = 5.0

            #FROM ABOVE + LEFT FREE
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from above going right")
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                print(17)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(16)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(15)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(14)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(13)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(12)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(11)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(10)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(9)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(8)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(7)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(6)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(5)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(4)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(3)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(2)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(1)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(0)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(-1)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                #print(self.whereCurrentAndInListOfPositions)
                print("done")
                
                self.vl = 5.0
                self.vr = 0.0
                self.vl = 5.0
                self.vr = 5.0
            
            
            
            
        
        #if the surrounding places on the map are all within the list that have been explored
        
        #LEFT AND ABOVE FILLED IN
        elif len(self.whereIveBeen) > 20 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list:
            
            
            
            #FROM BELOW + GOING RIGHT
            if self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from below 2")
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below 2+1")
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below -4")
                #print(16)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below -5")
                #print(15)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below -6")
                #print(14)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below -7")
                #print(13)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below -8")
                #print(12)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(11)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(10)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(9)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(8)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(7)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(6)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(5)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(4)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(3)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(2)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(1)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
               # print(self.whereCurrentAndInListOfPositions)
               # print("done")
                
                self.vl = 5.0
                self.vr = 0.0
                self.vl = 5.0
                self.vr = 5.0

            #FROM ABOVE + GOING TO RIGHT OF SCREEN
            elif self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count = 0
                
                
                print("from above + right 1")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 2")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 3")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 4")
                
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 5")
                
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 6")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 7")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 8")

                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 9")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 10")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 11")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 12")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 13")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 14")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 15")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 16")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from above + right 19")
                
                self.vl = 0.0
                self.vr = 5.0
                self.vl = 5.0
                self.vr = 5.0
            
            elif self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                
                print("from above + right 1")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 2")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 3")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 4")
                
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 5")
                
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 6")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 7")
                
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 8")

                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 9")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 10")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 11")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 12")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 13")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 14")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 15")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 16")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from above + right 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("from above + right 19")
                
                self.vl = 0.0
                self.vr = 5.0
                self.vl = 5.0
                self.vr = 5.0

        #ABOVE + BELOW CURRENT POSITION FILLED
        
        elif len(self.whereIveBeen) > 20 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list:

            if self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from below + left 1")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                #print(17)
                print("from below + left 2")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 3")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 4")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 5")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 6")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 7")
                
                self.vl = 0.0
                self.vr = 5.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 8")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 9")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 10")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 11")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 12")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 13")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 14")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 15")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 16")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 17")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print("from below + left 18")
                
                self.vl = 0.0
                self.vr = 5.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                print("done")
                
                self.vl = 0.0
                self.vr = 5.0
                self.vl = 5.0
                self.vr = 5.0

            #FROM ABOVE + LEFT FREE
            elif self.whereIveBeen[-2] != self.currentPosition and self.whereIveBeen[-2] == (xMapPosition, yMapPosition-1) and self.currentPosition not in self.whereCurrentAndInListOfPositions:
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                print("from above going right")
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
                print(17)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(16)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(15)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(14)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(13)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(12)
                
                self.vl = 5.0
                self.vr = 0.0

            elif self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(11)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(10)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(9)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(8)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(7)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(6)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(5)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(4)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(3)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(2)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(1)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(0)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-21] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-21] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                print(-1)
                
                self.vl = 5.0
                self.vr = 0.0
            elif self.whereIveBeen[-22] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-22] == (xMapPosition, yMapPosition-1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.whereCurrentAndInListOfPositions.clear()
                self.count -= 1
                #print(self.whereCurrentAndInListOfPositions)
                print("done")
                
                self.vl = 5.0
                self.vr = 0.0
                self.vl = 5.0
                self.vr = 5.0

        

        else:
            self.vl = 5.0
            self.vr = 5.0
            
            
        '''
        #FROM BELOW + GOING RIGHT WHEN ABOVE NOT FREE BUT LEFT AND RIGHT ARE FREE
        elif len(self.whereIveBeen) > 20 and (xMapPosition, yMapPosition-1) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list:
            #if self.currentPosition not in listOfPositions.list and self.currentPosition not in self.whereCurrentAndInListOfPositions:

            #if the surrounding places on the map are all within the list that have been explored
            if (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
                self.vl = 5.0
                self.vr = 5.0
                
            elif self.whereIveBeen[-2] != self.currentPosition and self.currentPosition not in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-2] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(self.whereIveBeen[-9])
                print("from below 3")
                
                self.vl = 5.0
                self.vr = 0.0

            if self.whereIveBeen[-3] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-3] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(self.whereIveBeen[-9])
                #print(self.whereIveBeen[-8])
               # print(17)
                
                self.vl = 5.0
                self.vr = 0.0

            if self.whereIveBeen[-4] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-4] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(16)
                
                self.vl = 5.0
                self.vr = 0.0

            if self.whereIveBeen[-5] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-5] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(15)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-6] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-6] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(14)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-7] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-7] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(13)
                
                self.vl = 5.0
                self.vr = 0.0

            if self.whereIveBeen[-8] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-8] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(12)
                
                self.vl = 5.0
                self.vr = 0.0

            if self.whereIveBeen[-9] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-9] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(11)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-10] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-10] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(10)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-11] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-11] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(9)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-12] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-12] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(8)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-13] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-13] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(7)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-14] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-14] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(6)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-15] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-15] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(5)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-16] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-16] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(4)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-17] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-17] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(3)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-18] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-18] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(2)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-19] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-19] == (xMapPosition, yMapPosition+1):
                
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
               # print(1)
                
                self.vl = 5.0
                self.vr = 0.0
            if self.whereIveBeen[-20] != self.currentPosition and self.currentPosition in self.whereCurrentAndInListOfPositions and self.whereIveBeen[-20] == (xMapPosition, yMapPosition+1):
                self.whereCurrentAndInListOfPositions.clear()
                self.whereCurrentAndInListOfPositions.append((xMapPosition, yMapPosition))
                self.count -= 1
                #print(self.whereCurrentAndInListOfPositions)
                #print("done")
                
                self.vl = 5.0
                self.vr = 0.0
            
            else:
                self.vl = 5.0
                self.vr = 5.0
        
        
        if (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
        '''
        

        
        

        

        
        
        
        
        
        '''
        #if the surrounding places on the map are all within the list that have been explored
        elif (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
            
            #print("all 4")
        
        elif (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) not in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
            #print("3")
        elif (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) not in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
            #print("3")
        elif (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) not in listOfPositions.list and (xMapPosition, yMapPosition-1) in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
            #print("3")
        elif (xMapPosition, yMapPosition) in listOfPositions.list and (xMapPosition+1, yMapPosition) in listOfPositions.list and (xMapPosition-1, yMapPosition) in listOfPositions.list and (xMapPosition, yMapPosition+1) in listOfPositions.list and (xMapPosition, yMapPosition-1) not in listOfPositions.list:
            self.vl = 5.0
            self.vr = 5.0
            #print("3")
            #print("been there before!")
            '''
        
        
            

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

def register(canvas):
    registryActives = []
    registryPassives = []
    noOfBots = 1
    noOfDirt = 300
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i),canvas)
        registryActives.append(bot)
        bot.draw(canvas)
    for i in range(0,noOfDirt):
        dirt = Dirt("Dirt"+str(i))
        registryPassives.append(dirt)
        dirt.draw(canvas)
    count = Counter()
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,registryActives) )
    return registryActives, registryPassives, count

def moveIt(canvas,registryActives,registryPassives,count,moves):
    moves += 1
    for rr in registryActives:
        chargerIntensityL, chargerIntensityR = rr.senseCharger(registryPassives)
        rr.brain(chargerIntensityL, chargerIntensityR)
        rr.move(canvas,registryPassives,1.0)
        registryPassives = rr.collectDirt(canvas,registryPassives, count)
        numberOfMoves = 1000
        if moves>numberOfMoves:
            print("total dirt collected in",numberOfMoves,"moves is",count.dirtCollected, (listOfPositions.list.sort))
            sys.exit()
    canvas.after(50,moveIt,canvas,registryActives,registryPassives,count,moves)

def main():
    window = tk.Tk()
    canvas = initialise(window)
    registryActives, registryPassives, count = register(canvas)
    moves = 0
    moveIt(canvas,registryActives,registryPassives, count, moves)
    window.mainloop()

main()

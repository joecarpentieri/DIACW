from playsound import playsound
from PIL import Image, ImageTk
import tkinter as tk
import random
import math
import numpy as np
import time
import sys
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

class WhereTheyveBeen():

    def __init__(self):
        self.listOfWhere = []

where = WhereTheyveBeen()

class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.turningCount = 0
        self.movingCount = random.randrange(50,100)
        self.currentlyTurning = False
        self.time = 0
        self.trainingSet = []
        self.dangerThreshold = 0
        self.currentPosition = 0

    # modify this to change the robot's behaviour
    def thinkAndAct(self, chargerL, chargerR, x, y, sl, sr,\
                    count, xMapPosition, yMapPosition, whereIveBeen):
        completed = False
        newX = None
        newY = None
        
        #self.drawMap()

        #print(self.currentPosition)

        speedLeft = 2.0
        speedRight = 2.0
        
        # wandering behaviour
        '''if self.currentlyTurning==True:
            speedLeft = -2.0
            speedRight = 2.0
            self.turningCount -= 1
        else:
            speedLeft = 2.0
            speedRight = 2.0
            self.movingCount -= 1
        if self.movingCount==0 and not self.currentlyTurning:
            self.turningCount = random.randrange(20,40)
            self.currentlyTurning = True
        if self.turningCount==0 and self.currentlyTurning:
            self.movingCount = random.randrange(50,100)
            self.currentlyTurning = False'''

        if abs(chargerR-chargerL)<chargerL*0.1 and not self.currentlyTurning and (chargerL+chargerR)<250: #approximately the same
            speedLeft = 2.0
            speedRight = 2.0
        if 160<chargerL<400 and chargerL>chargerR and not self.currentlyTurning:
            speedLeft = 2.0
            speedRight = 0.0
            if len(where.listOfWhere) > 2:
                if where.listOfWhere[-1] == (xMapPosition, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition):
                    #print("TURNING!")
                    pass
                else:
                    print("other side!")
                    print(where.listOfWhere[-1])
                    print(where.listOfWhere[-2])
                    print(xMapPosition, yMapPosition)
                    #print(where.listOfWhere)
        if 160<chargerR<400 and chargerR>chargerL and not self.currentlyTurning:
            speedLeft = 0.0
            speedRight = 2.0
            if len(where.listOfWhere) > 2:
                if where.listOfWhere[-1] == (xMapPosition, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition+1, yMapPosition-2) or where.listOfWhere[-1] == (xMapPosition-1, yMapPosition+2) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition+2, yMapPosition-1) or where.listOfWhere[-1] == (xMapPosition-2, yMapPosition+1) or where.listOfWhere[-1] == (xMapPosition, yMapPosition):
                    pass
                else:
                    print("other side!")
                    print(where.listOfWhere[-1])
                    print(where.listOfWhere[-2])
                    print(xMapPosition, yMapPosition)
                    #print(where.listOfWhere)
        if chargerR+chargerL>1000:
            speedLeft = 2.0
            speedRight = 2.0

        if self.time==1000:
            print("complete: total dirt collected "+str(count))
            completed = True

        #toroidal geometry
        if x>1000:
            newX = 0
        if x<0:
            newX = 1000
        if y>1000:
            newY = 0
        if y<0:
            newY = 1000


       

        self.time += 1

        return speedLeft, speedRight, newX, newY, count, completed, xMapPosition, yMapPosition, whereIveBeen

class Bot():

    def __init__(self,namep,canvasp, counterp):
        self.name = namep
        self.canvas = canvasp
        self.x = random.randint(100,900)
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        #self.theta = 0
        self.ll = 60 #axle width
        self.sl = 0.0
        self.sr = 0.0
        self.battery = 1000
        self.counter = counterp
        self.map = np.zeros( (10,10) )
        self.xMapPosition = 0
        self.yMapPosition = 0
        self.whereIveBeen = []

    def getLocation(self):
        return self.x, self.y
    
    def updateMap(self):
        xMapPosition = int(math.floor(self.x/100))
        self.xMapPosition = xMapPosition
        yMapPosition = int(math.floor(self.y/100))
        self.yMapPosition = yMapPosition
        self.map[xMapPosition][yMapPosition] = 1
        self.currentPosition = (xMapPosition, yMapPosition)
        #self.drawMap()
        self.whereIveBeen.append((xMapPosition, yMapPosition))
        #print(self.whereIveBeen)
        where.listOfWhere.append(self.currentPosition)
        #print(self.whereIveBeen)
        #print(listOfPositions.list)
        #print(self.currentPosition)
        #print(self.currentPosition)

    def thinkAndAct(self, agents, passiveObjects, canvas):
        chargerL, chargerR = self.senseBots(agents)

        #view = self.look(agents)
        self.sl, self.sr, xx, yy, count, completed, self.xMapPosition, self.yMapPosition, self.whereIveBeen = self.brain.thinkAndAct\
            (chargerL, chargerR, self.x, self.y, \
             self.sl, self.sr, self.counter.dirtCollected, self.xMapPosition, self.yMapPosition, self.whereIveBeen)
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        if completed:
            return count
        else:
            return None
        
    def setBrain(self,brainp):
        self.brain = brainp

    #returns sensors values that detect chargers
    def senseBots(self, agents):
        chargerL = 0.0
        chargerR = 0.0
        for pp in agents:
            if isinstance(pp, Bot):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                chargerL += 200000/(distanceL*distanceL)
                chargerR += 200000/(distanceR*distanceR)
        #print(chargerL, chargerR)
        return chargerL, chargerR

    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2) )

    # what happens at each timestep
    def update(self,canvas,passiveObjects,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.battery -= 1
        if self.battery<=0:
            self.battery = 0
        self.move(canvas,dt)

    # draws the robot at its current position
    def draw(self,canvas):

        '''self.cameraPositions = []
        for pos in range(20,-21,-5):
            self.cameraPositions.append( ( (self.x + pos*math.sin(self.theta)) + 30*math.sin((math.pi/2.0)-self.theta), \
                                 (self.y - pos*math.cos(self.theta)) + 30*math.cos((math.pi/2.0)-self.theta) ) )
        for xy in self.cameraPositions:
            canvas.create_oval(xy[0]-2,xy[1]-2,xy[0]+2,xy[1]+2,fill="purple1",tags=self.name)
        for xy in self.cameraPositions:
            canvas.create_line(xy[0],xy[1],xy[0]+400*math.cos(self.theta),xy[1]+400*math.sin(self.theta),fill="light grey",tags=self.name)'''
            

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
        canvas.create_oval(centre1PosX-16,centre1PosY-16,\
                           centre1PosX+16,centre1PosY+16,\
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

    # handles the physics of the movement
    # cf. Dudek and Jenkin, Computational Principles of Mobile Robotics
    def move(self,canvas,dt):
        if self.battery==0:
            self.sl = 0
            self.sl = 0
        if self.sl==self.sr:
            R = 0
        else:
            R = (self.ll/2.0)*((self.sr+self.sl)/(self.sl-self.sr))
        omega = (self.sl-self.sr)/self.ll
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
        if self.sl==self.sr: # straight line movement
            self.x += self.sr*math.cos(self.theta) #sr wlog
            self.y += self.sr*math.sin(self.theta)
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

    def collectDirt(self, canvas, passiveObjects, count):
        toDelete = []
        for idx,rr in enumerate(passiveObjects):
            if isinstance(rr,Dirt):
                if self.distanceTo(rr)<30:
                    canvas.delete(rr.name)
                    toDelete.append(idx)
                    count.itemCollected(canvas)
        for ii in sorted(toDelete,reverse=True):
            del passiveObjects[ii]
        return passiveObjects

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


def initialise(window):
    window.resizable(False,False)
    canvas = tk.Canvas(window,width=1000,height=1000)
    canvas.pack()
    return canvas

def buttonClicked(x,y,agents):
    for rr in agents:
        if isinstance(rr,Bot):
            rr.x = x
            rr.y = y

def createObjects(canvas,noOfBots=2,noOfLights=2,amountOfDirt=300,noOfCats=5):
    agents = []
    passiveObjects = []

    count = Counter()
    
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i),canvas,count)
        brain = Brain(bot)
        bot.setBrain(brain)
        agents.append(bot)
        bot.draw(canvas)

    for i in range(0,noOfCats):
        cat = Cat("Cat"+str(i),canvas)
        agents.append(cat)
        cat.draw(canvas)

    for i in range(0,noOfLights):
        lamp = Lamp("Lamp"+str(i))
        passiveObjects.append(lamp)
        lamp.draw(canvas)
    
    

    for i in range(0,amountOfDirt):
        dirt = Dirt("Dirt"+str(i))
        passiveObjects.append(dirt)
        dirt.draw(canvas)
    
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,agents) )
    
    return agents, passiveObjects, count

def quit():
    tk.destroy()

def moveIt(canvas,agents,passiveObjects,count,window):
    for rr in agents:
        returnedCount = rr.thinkAndAct(agents,passiveObjects, canvas)
        if returnedCount != None:
            window.destroy()
            return returnedCount
        rr.update(canvas,passiveObjects,1.0)
        if isinstance(rr,Bot):
            passiveObjects = rr.collectDirt(canvas,passiveObjects,count)
        
        #if moves==100:
            #return moves
        #     time.sleep(3)
            
    canvas.after(20,moveIt,canvas,agents,passiveObjects,count,window)


def runMain(botNo, dirtNo):
    window = tk.Tk()
    canvas = initialise(window)
    agents, passiveObjects, count = createObjects(canvas,noOfBots=botNo,noOfLights=0,amountOfDirt=dirtNo,noOfCats=0)
    moves = moveIt(canvas,agents,passiveObjects,count,window)
    
    window.mainloop()
    return count.getDirtCollected()

#main()


def runMainMultiple(noOfTimes, botNo, dirtNo):
    counterList = []
    for times in range(noOfTimes):
        counterList.append(runMain(botNo, dirtNo))
    return counterList

#print(runMainMultiple(2, 20, 300))

#Running with different parameters

def runExperimentsWithDifferentParameters():
    resultsTable = {}
    for condition in [1,2]:
        dirtCollectedList = runMainMultiple(1,condition, 300)
        resultsTable[condition] = dirtCollectedList
    print(resultsTable)
    results = pd.DataFrame(resultsTable)
    print(results)
    results.to_excel("roboticsExperiment.xlsx")
    print(ttest_ind(results[1], results[2]))
    print(results.mean(axis=0))
    results.boxplot(grid=True)
    plt.show()

print(runExperimentsWithDifferentParameters())
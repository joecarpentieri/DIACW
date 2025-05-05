from playsound import playsound
from PIL import Image, ImageTk
import tkinter as tk
import random
import math
import numpy as np
import time
import sys

class Brain():

    def __init__(self,botp):
        self.bot = botp
        self.turningCount = 0
        self.movingCount = random.randrange(50,100)
        self.currentlyTurning = False
        self.time = 0
        self.trainingSet = []
        self.dangerThreshold = 0

    # modify this to change the robot's behaviour
    def thinkAndAct(self, lightL, lightR, chargerL, chargerR, x, y, sl, sr,\
                    battery, collision):
        
        newX = None
        newY = None
        
        # wandering behaviour
        if self.currentlyTurning==True:
            speedLeft = -2.0
            speedRight = 2.0
            self.turningCount -= 1
        else:
            speedLeft = 5.0
            speedRight = 5.0
            self.movingCount -= 1
        if self.movingCount==0 and not self.currentlyTurning:
            self.turningCount = random.randrange(20,40)
            self.currentlyTurning = True
        if self.turningCount==0 and self.currentlyTurning:
            self.movingCount = random.randrange(50,100)
            self.currentlyTurning = False

        #battery - these are later so they have priority
    
        if chargerR>170:
            print(chargerR)
        if chargerL>170:
            print(chargerL)
            '''
            if chargerR>chargerL:
                speedLeft = 2.0
                speedRight = -2.0
                print("can sense bot!")
            elif chargerR<chargerL:
                speedLeft = -2.0
                speedRight = 2.0
                print("can sense bot!")
            '''
            '''if abs(chargerR-chargerL)<chargerL*0.1 and not (chargerR+chargerL)>350: #approximately the same
                speedLeft = 5.0
                speedRight = 5.0'''
            '''if abs(chargerR-chargerL)<chargerL*0.1 and (chargerR+chargerL)>350:
                speedLeft = 5.0
                speedRight = 0.0
                print(chargerL+chargerR)'''
        if chargerR>175:
            speedLeft = 0.0
            speedRight = 5.0
            '''if chargerL>250:
                speedLeft = 0.0
                speedRight = 5.0'''
        if chargerL+chargerR>200 and battery<1000:
            print("can sense bot!")
        '''if chargerL+chargerR>200 and battery<1000:
             speedLeft = 0.0
             speedRight = 0.0
             speedRight = 0.0'''



        '''if chargerL+chargerR>500:
            if chargerR>chargerL:
                speedLeft = 2.0
                speedRight = 0.0
                print("can sense bot!")
                print(chargerL+chargerR)
        if chargerL+chargerR>1000:
            speedLeft = 5.0
            speedRight = 5.0'''

        '''elif chargerR<chargerL:
                speedLeft = -2.0
                speedRight = 0.0
                print("can sense bot!")'''
        '''if abs(chargerR-chargerL)<chargerL*0.1: #approximately the same
                speedLeft = 5.0
                speedRight = 5.0
                print("can sense bot!")'''
        '''if lightR+lightL>300:
                speedLeft = 5.0
                speedRight = 0.0
                print("can sense light!")'''
        '''if chargerL+chargerR>200 and battery<1000:
            speedLeft = 0.0
            speedRight = 0.0'''

        #toroidal geometry
        if x>1000:
            newX = 0
        if x<0:
            newX = 1000
        if y>1000:
            newY = 0
        if y<0:
            newY = 1000

        

        return speedLeft, speedRight, newX, newY

class Bot():

    def __init__(self,namep,canvasp):
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

    def getLocation(self):
        return self.x, self.y

    def thinkAndAct(self, agents, passiveObjects, canvas):
        lightL, lightR = self.senseLight(passiveObjects)
        chargerL, chargerR = self.senseBots(agents)
        collision = self.collision(agents)

        #view = self.look(agents)
        self.sl, self.sr, xx, yy = self.brain.thinkAndAct\
            (lightL, lightR, chargerL, chargerR, self.x, self.y, \
             self.sl, self.sr, self.battery, collision)
        if xx != None:
            self.x = xx
        if yy != None:
            self.y = yy
        
    def setBrain(self,brainp):
        self.brain = brainp

    def reactToDanger(self, agents):
        print("dangerous situation")
        playsound("436589__julien-matthey__jm-transport-ext-horn-01a-car-short-mini-countryman.wav", block=False)
        for ag in agents:
            if isinstance(ag,Cat):
                ag.jump(big=True)


    '''def look(self,agents):
        self.view = [0]*9
        for idx,pos in enumerate(self.cameraPositions):
            for cc in agents:
                if isinstance(cc,Cat):
                    dd = self.distanceTo(cc)
                    scaledDistance = max(400-dd,0)/400
                    ncx = cc.x-pos[0] #cat if robot were at 0,0
                    ncy = cc.y-pos[1]
                    #print(abs(angle-self.theta)%2.0*math.pi)
                    m = math.tan(self.theta)
                    A = m*m+1
                    B = 2*(-m*ncy-ncx)
                    r = 15 #radius
                    C = ncy*ncy - r*r + ncx*ncx 
                    if B*B-4*A*C>=0 and scaledDistance>self.view[idx]:
                        self.view[idx] = scaledDistance
        self.canvas.delete("view")
        for vv in range(9):
            if self.view[vv]==0:
                self.canvas.create_rectangle(850+vv*15,50,850+vv*15+15,65,fill="white",tags="view")
            if self.view[vv]>0:
                colour = hex(15-math.floor(self.view[vv]*16.0)) #scale to 0-15 -> hex
                fillHex = "#"+colour[2]+colour[2]+colour[2]
                self.canvas.create_rectangle(850+vv*15,50,850+vv*15+15,65,fill=fillHex,tags="view")
        return self.view'''


    #returns the output from polling the light sensors
    def senseLight(self, passiveObjects):
        lightL = 0.0
        lightR = 0.0
        for pp in passiveObjects:
            if isinstance(pp,Lamp):
                lx,ly = pp.getLocation()
                distanceL = math.sqrt( (lx-self.sensorPositions[0])*(lx-self.sensorPositions[0]) + \
                                       (ly-self.sensorPositions[1])*(ly-self.sensorPositions[1]) )
                distanceR = math.sqrt( (lx-self.sensorPositions[2])*(lx-self.sensorPositions[2]) + \
                                       (ly-self.sensorPositions[3])*(ly-self.sensorPositions[3]) )
                lightL += 200000/(distanceL*distanceL)
                lightR += 200000/(distanceR*distanceR)
        return lightL, lightR

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
        return chargerL, chargerR

    def distanceTo(self,obj):
        xx,yy = obj.getLocation()
        return math.sqrt( math.pow(self.x-xx,2) + math.pow(self.y-yy,2) )

    # what happens at each timestep
    def update(self,canvas,passiveObjects,dt):
        # for now, the only thing that changes is that the robot moves
        #   (using the current settings of self.sl and self.sr)
        self.battery -= 1
        for rr in passiveObjects:
            if isinstance(rr,Charger) and self.distanceTo(rr)<80:
                self.battery += 10
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

    def collision(self,agents):
        collision = False
        for rr in agents:
            if isinstance(rr,Cat):
                if self.distanceTo(rr)<50.0:
                    playsound("385892__spacether__262312-steffcaffrey-cat-meow1.mp3",block=False)
                    collision = True
                    rr.jump()
        return collision

class Cat:
    def __init__(self,namep,canvasp):
        self.x = random.randint(100,900)
        self.y = random.randint(100,900)
        self.theta = random.uniform(0.0,2.0*math.pi)
        self.name = namep
        self.canvas = canvasp
        self.vl = 1.0
        self.vr = 1.0
        self.turning = 0
        self.moving = random.randrange(50,100)
        self.currentlyTurning = False
        self.ll = 20
        imgFile = Image.open("cat.png")
        imgFile = imgFile.resize((30,30))
        self.image = ImageTk.PhotoImage(imgFile)
        
    def draw(self,canvas):
        body = canvas.create_image(self.x,self.y,image=self.image,tags=self.name)

    def getLocation(self):
        return self.x, self.y

    def thinkAndAct(self, agents, passiveObjects, canvas):
        # wandering behaviour
        if self.currentlyTurning==True:
            self.vl = -2.0
            self.vr = 2.0
            self.turning -= 1
        else:
            self.vl = 1.0
            self.vr = 1.0
            self.moving -= 1
        if self.moving==0 and not self.currentlyTurning:
            self.turning = random.randrange(20,40)
            self.currentlyTurning = True
        if self.turning==0 and self.currentlyTurning:
            self.moving = random.randrange(50,100)
            self.currentlyTurning = False

    def update(self,canvas,passiveObjects,dt):
        self.move(canvas,dt)
            
    def move(self,canvas,dt):
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
        #self.updateMap()
        canvas.delete(self.name)
        self.draw(canvas)

    def jump(self,big=False):
        if not big:
            self.x += random.randint(20,50)
            self.y += random.randint(20,50)
        else:
            self.x += random.randint(50,100)
            self.y += random.randint(50,100)
        if self.x<0.0:
            self.x=999.0
        if self.x>1000.0:
            self.x = 0.0
        if self.y<0.0:
            self.y=999.0
        if self.y>1000.0:
            self.y = 0.0
        #self.updateMap()
        self.canvas.delete(self.name)
        self.draw(self.canvas)
        

class Lamp():
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="yellow",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

class Charger():
    def __init__(self,namep):
        self.centreX = random.randint(100,900)
        self.centreY = random.randint(100,900)
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="red",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

class WiFiHub:
    def __init__(self,namep,xp,yp):
        self.centreX = xp
        self.centreY = yp
        self.name = namep
        
    def draw(self,canvas):
        body = canvas.create_oval(self.centreX-10,self.centreY-10, \
                                  self.centreX+10,self.centreY+10, \
                                  fill="purple",tags=self.name)

    def getLocation(self):
        return self.centreX, self.centreY

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
    
    for i in range(0,noOfBots):
        bot = Bot("Bot"+str(i),canvas)
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

    charger = Charger("Charger"+str(i))
    passiveObjects.append(charger)
    charger.draw(canvas)
    
    hub1 = WiFiHub("Hub1",950,50)
    passiveObjects.append(hub1)
    hub1.draw(canvas)
    hub2 = WiFiHub("Hub2",50,500)
    passiveObjects.append(hub2)
    hub2.draw(canvas)

    for i in range(0,amountOfDirt):
        dirt = Dirt("Dirt"+str(i))
        passiveObjects.append(dirt)
        dirt.draw(canvas)

    count = Counter()
    
    canvas.bind( "<Button-1>", lambda event: buttonClicked(event.x,event.y,agents) )
    
    return agents, passiveObjects, count

def moveIt(canvas,agents,passiveObjects,count,moves):
    for rr in agents:
        rr.thinkAndAct(agents,passiveObjects,canvas)
        rr.update(canvas,passiveObjects,1.0)
        if isinstance(rr,Bot):
            passiveObjects = rr.collectDirt(canvas,passiveObjects,count)
        # moves +=1
        # if moves==5000:
        #     time.sleep(3)
        #     sys.exit()
    canvas.after(20,moveIt,canvas,agents,passiveObjects,count,moves)

def main():
    window = tk.Tk()
    canvas = initialise(window)
    agents, passiveObjects, count = createObjects(canvas,noOfBots=20,noOfLights=1,amountOfDirt=300,noOfCats=0)
    moveIt(canvas,agents,passiveObjects,count,0)
    window.mainloop()

main()

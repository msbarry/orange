# 
# OWTools.py
# tools for Visual Orange
#

TRUE=1
FALSE=0

from qt import *
from random import *

#A 10X10 single color pixmap
class ColorPixmap (QPixmap):
    def __init__(self,color=Qt.white):
        "Creates a single-color pixmap"
        QPixmap.__init__(self,10,10)
        self.fill(color)

  
#A dynamic tool tip class      
class DynamicToolTip (QToolTip):

    def __init__(self,parent=None):
        "Creates a new dynamic tool tip."
        QToolTip.__init__(self,parent)
        self.rects=[]
        self.texts=[]
    
    def addToolTip(self,rect,text):
        "Adds a tool tip. If a tooltip with the same name already exists, it updates it instead of adding a new one."
        if text in self.texts:
            self.rects[self.texts.index(text)]=rect
        else:
            self.rects.append(rect)
            self.texts.append(text)
    
    def maybeTip(self,point):
        "Decides whether to pop up a tool tip and which text to pop up"
        for i in range(len(self.rects)):
            if self.rects[i].contains(point):
                self.tip(self.rects[i],self.texts[i])
                break #first rect in which the point is prevails
                
    def removeAll(self):
        self.rects=[]
        self.texts=[]


class QPointFloat:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class QRectFloat:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        

#A dynamic tool tip class      
class DynamicToolTipFloat:
    def __init__(self):
        self.rects=[]
        self.texts=[]
    
    def addToolTip(self,rect,text):
        "Adds a tool tip. If a tooltip with the same name already exists, it updates it instead of adding a new one."
        self.rects.append(rect)
        self.texts.append(text)
    
    def maybeTip(self, x, y):
        "Decides whether to pop up a tool tip and which text to pop up"
        for i in range(len(self.rects)):
            rect = self.rects[i]
            if x > rect.x and y > rect.y and x < rect.x + rect.width and y < rect.y + rect.height:
                return self.texts[i]
        return ""

                    
    def removeAll(self):
        self.rects=[]
        self.texts=[]        
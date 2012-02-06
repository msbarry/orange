"""
<name>Net from Distances</name>
<description>Costructs Graph object by connecting nodes from ExampleTable where distance between them is between given threshold.</description>
<icon>icons/NetworkFromDistances.png</icon>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact> 
<priority>6440</priority>
"""

#
# OWNetworkFromDistances.py
#

import copy
import random

import Orange
import OWGUI

from OWNxHist import *
from OWWidget import *
from OWGraph import *
from OWHist import *

class OWNxFromDistances(OWWidget, OWNxHist):
    settingsList=["spinLowerThreshold", "spinUpperThreshold", "netOption", 
                  "dstWeight", "kNN", "andor", "excludeLimit"]
    
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, "Nx from Distances")
        OWNxHist.__init__(self)
        
        self.inputs = [("Distances", Orange.core.SymMatrix, self.setMatrix)]
        self.outputs = [("Network", Orange.network.Graph), 
                        ("Data", Orange.data.Table), 
                        ("Distances", Orange.core.SymMatrix)]

        self.addHistogramControls()
        
        # get settings from the ini file, if they exist
        self.loadSettings()
        
        # GUI
        # general settings
        boxHistogram = OWGUI.widgetBox(self.mainArea, box = "Distance histogram")
        self.histogram = OWHist(self, boxHistogram)
        boxHistogram.layout().addWidget(self.histogram)

        boxHistogram.setMinimumWidth(500)
        boxHistogram.setMinimumHeight(300)
        
        # info
        boxInfo = OWGUI.widgetBox(self.controlArea, box = "Network info")
        self.infoa = OWGUI.widgetLabel(boxInfo, "No data loaded.")
        self.infob = OWGUI.widgetLabel(boxInfo, '')
        self.infoc = OWGUI.widgetLabel(boxInfo, '')
        
        OWGUI.rubber(self.controlArea)
        
        self.resize(700, 100)

    def sendReport(self):
        self.reportSettings("Settings",
                            [("Edge thresholds", "%.5f - %.5f" % \
                              (self.spinLowerThreshold, \
                               self.spinUpperThreshold)),
                             ("Selected vertices", ["All", \
                                "Without isolated vertices", 
                                "Largest component", 
                                "Connected with vertex"][self.netOption]),
                             ("Weight", ["Distance", "1 - Distance"][self.dstWeight])])
        self.reportSection("Histogram")
        self.reportImage(self.histogram.saveToFileDirect, QSize(400,300))
        self.reportSettings("Output graph",
                            [("Vertices", self.matrix.dim),
                             ("Edges", self.nedges),
                             ("Connected vertices", "%i (%.1f%%)" % \
                              (self.pconnected, self.pconnected / \
                               max(1, float(self.matrix.dim))*100))])
        
    def sendSignals(self):
        if self.graph != None:
            #setattr(matrix, "items", self.graph.items)
            self.matrix.items = self.graph.items()
        
        self.send("Network", self.graph)
        
        if self.matrix:
            self.send("Distances", self.matrix)
            
        if self.graph == None:
            self.send("Data", None)
        else:
            self.send("Data", self.graph.items())
                                                                     
if __name__ == "__main__":    
    appl = QApplication(sys.argv)
    ow = OWNxFromDistances()
    ow.show()
    appl.exec_()
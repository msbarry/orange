"""
<name>Data Sampler (A)</name>
<description>Randomly selects a subset of instances from the data set</description>
<icon>icons/DataSamplerA.png</icon>
<priority>10</priority>
"""
from OWWidget import *
import OWGUI

class OWDataSamplerA(OWWidget):
    
    def __init__(self, parent=None):
        OWWidget.__init__(self, parent, 'SampleData')
        
        self.inputs = [("Data", ExampleTable, self.data)]
        self.outputs = [("Sampled Data", ExampleTable)]

        # GUI
        box = QVGroupBox("Info", self.controlArea)
        self.infoa = QLabel('No data on input yet, waiting to get something.', box)
        self.infob = QLabel('', box)
        self.resize(100,50)

    def data(self, dataset):
        if dataset:
            self.infoa.setText('%d instances in input data set' % len(dataset))
            indices = orange.MakeRandomIndices2(p0=0.1)
            ind = indices(dataset)
            sample = dataset.select(ind, 0)
            self.infob.setText('%d sampled instances' % len(sample))
            self.send("Sampled Data", sample)
        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('', box)
            self.send("Sampled Data", None)
            

##############################################################################
# Test the widget, run from prompt

if __name__=="__main__":
    appl = QApplication(sys.argv)
    ow = OWDataSamplerA()
    appl.setMainWidget(ow)
    ow.show()
    dataset = orange.ExampleTable('iris.tab')
    ow.data(dataset)
    appl.exec_loop()

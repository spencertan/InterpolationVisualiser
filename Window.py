from MainWindow import *
from PySide6.QtWidgets import QMessageBox, QFileDialog, QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from GraphContext import *
import os



class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        #Initialise & Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.newfile.clicked.connect(self.newFile) 
        self.ui.openfile.clicked.connect(self.openFile) 
        self.ui.open_menu.clicked.connect(self.openMenu) 

        #Setup GraphContext
        self.graph = GraphContext(self.ui.graph, self.ui.verticalLayout_8)

    def newFile(self):
        self.graph.clear()

    def newtonRead(self,lines):

        for [i,line] in enumerate(lines):
            if i == 0 or i >= self.graph.max_point:
                continue
            parse = line.split(' ')

            if len(parse) == 2:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]))
            elif len(parse) == 3:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),m=float(parse[2]))
            elif len(parse) == 4:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=float(parse[2]),vy=float(parse[3]))
            elif len(parse) == 5:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=float(parse[2]),vy=float(parse[3]),m=float(parse[4]))
            elif len(parse) == 6:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=float(parse[2]),vy=float(parse[3]),ax=float(parse[4]),ay=float(parse[5]))
            elif len(parse) == 7:
                self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=float(parse[2]),vy=float(parse[3]),ax=float(parse[4]),ay=float(parse[5]),m=float(parse[6]))

    def bezierRead(self,lines):

        rvx = rvy = rax = ray = None
        for [i,line] in enumerate(lines):
            if i == 0 or i >= self.graph.max_point:
                continue

            parse = line.split(' ')

            if i == 1:
                if len(parse) == 2:
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]))
                elif len(parse) == 3:
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),m=float(parse[2]))
                elif len(parse) == 6:
                    rvx = float(parse[2])
                    rvy = float(parse[3])
                    rax = float(parse[4])
                    ray = float(parse[5])
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=rvx,vy=rvy,ax=rax,ay=ray)
                elif len(parse) == 7:
                    rvx = float(parse[2])
                    rvy = float(parse[3])
                    rax = float(parse[4])
                    ray = float(parse[5])
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=rvx,vy=rvy,ax=rax,ay=ray,m=float(parse[6]))
            else:
                if len(parse) == 2:
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=rvx,vy=rvy,ax=rax,ay=ray)
                elif len(parse) == 3:
                    self.graph.addPoint(px=float(parse[0]),py=float(parse[1]),vx=rvx,vy=rvy,ax=rax,ay=ray,m=float(parse[2]))

            
    def openFile(self):
        result = QFileDialog.getOpenFileName(caption="Select a file",
                                             dir=os.getcwd(),
                                             filter="Input File (*.txt)")
        if not result[0]:
            return

        self.graph.clear()

        with open(result[0], 'r') as file:
            lines = file.readlines()
            if self.graph.interpolation_type == InterpolationType.NEWTON:
                self.newtonRead(lines)
            elif self.graph.interpolation_type == InterpolationType.BEZIER:
                self.bezierRead(lines)


    def openMenu(self):
        width = self.ui.side_menu_wrapper.width()

        if width == 0:
            new_width = 400
            self.ui.open_menu.setIcon(QIcon(u"UI/back.svg"))
        else:
            new_width = 0
            self.ui.open_menu.setIcon(QIcon(u"UI/menu.svg"))
        
        self.animation = QPropertyAnimation(self.ui.side_menu_wrapper, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
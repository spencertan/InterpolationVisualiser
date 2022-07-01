import enum
from os import truncate
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PointDetailWidget import *
from Math import *

class SelectionType(enum.Enum):
    POINT = 1
    VEL = 2
    ACC = 3

class Point:
    def __init__(self, px, py, vx=None, vy=None, ax=None,ay=None,m=1):
        self.p = [px,py]
        self.v = [vx,vy] if vx is not None else None
        self.a = [ax,ay] if ax is not None else None
        self.m = m
    
    def __iter__(self):
        return iter((self.p,self.v,self.a,self.m))

class GraphContext:
    def __init__(self,graph:pg.PlotWidget,points_ui:QVBoxLayout):

        pg.setConfigOption('leftButtonPan', False)
        self.points= []
        self.interpolant = [],[]
        self.sample = [],[]

        """
        The following are default information used to set-up the grid
        """
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.points_ui = points_ui
        self.points_ui.setAlignment(Qt.AlignTop)
        self.graph = graph
        self.vb = self.graph.plotItem.vb
        self.graph.showGrid(x=True,y=True,alpha=0.3)
        self.graph.setMouseEnabled(True,True)
        self.graph.setMenuEnabled(False)
        self.graph.setLabel("left", "Y-Values", units="y")
        self.graph.setLabel("bottom", "X-Values", units="x")
        self.graph.setXRange(-20,20)
        self.graph.setYRange(-20,20)
        """
        Setting up mouse events
        The following connects callback to the signal for mouse movement to record cursor position

        While Press/Released events are wrapped in order to handle click-and-drag motion which
        the built-in signals only detects mouse released to register mouse press, hence click-drag motion is not allowed
        """
        #Connect Mouse Events
        self.graph.scene().sigMouseMoved.connect(self.sceneMouseMoved)

        #internal click/release mouse events
        self.click_scale = 1.0
        self.internalMousePressEvent = self.graph.mousePressEvent
        self.internalMouseReleaseEvent = self.graph.mouseReleaseEvent 
        self.internalMouseDoubleClickEvent = self.graph.mouseDoubleClickEvent
        self.graph.sigRangeChanged.connect(self.rangeUpdate)
        #rebind click/release mouse events with wrapper
        self.graph.mousePressEvent = self.mousePressWrapper
        self.graph.mouseReleaseEvent = self.mouseReleaseWrapper
        self.graph.mouseDoubleClickEvent = self.mouseDoubleClickWrapper

        range_ = self.graph.getViewBox().viewRange() 
        self.graph.getViewBox().setLimits(xMin=-100.0, xMax=100.0,yMin=-100.0, yMax=100.0)  

        self.type = None
        self.index = None
        self.RMB = False

        #plot
        self.vel_vector = pg.PlotDataItem(name = 'Velocity Vector',pen=pg.mkPen('y',width=2, style=Qt.DotLine),pxMode=True)
        self.acc_vector = pg.PlotDataItem(name = 'Acceleration Vector',pen=pg.mkPen('g',width=2, style=Qt.DotLine),pxMode=True)
        self.graph.addItem(self.vel_vector)
        self.graph.addItem(self.acc_vector)
        self.graph.addLegend(pen='w')

        self.point_scatter = pg.PlotDataItem(name = 'Points',pen=None,symbolPen='b', pxMode=True, symbol='crosshair', size=10)
        self.vel_scatter = pg.PlotDataItem(name = 'Velocity',pen=None,symbolPen='y', pxMode=True, symbol='x', size=5)
        self.acc_scatter = pg.PlotDataItem(name = 'Acceleration',pen=None,symbolPen='g', pxMode=True, symbol='x', size=5)
        self.curve_plot = pg.PlotDataItem(name = 'Curve', pen='r',  pxMode=True)

        self.graph.addItem(self.point_scatter)
        self.graph.addItem(self.vel_scatter)
        self.graph.addItem(self.acc_scatter)
        self.graph.addItem(self.curve_plot)
        font = QFont()
        font.setPixelSize(12)
        self.coords =[]
        for i in range(30):
            text = pg.TextItem()
            text.setVisible(False)
            text.setFont(font)
            self.coords.append(text)
            self.graph.addItem(text)
            
    def mousePressWrapper(self, ev):
        self.internalMousePressEvent(ev)
        self.sceneMousePress(ev)
    
    def mouseDoubleClickWrapper(self, ev):
        self.internalMouseDoubleClickEvent(ev)
        self.sceneMouseDoubleClick(ev)

    def mouseReleaseWrapper(self,ev):
        self.internalMouseReleaseEvent(ev)
        self.sceneMouseRelease(ev)

    def sceneMouseMoved(self, pos):
        mouse_point = self.vb.mapSceneToView(pos)
        self.mouse_x = clamp(np.round(mouse_point.x(),2),-100.0,100.0)
        self.mouse_y = clamp(np.round(mouse_point.y(),2),-100.0,100.0)

        if self.type is not None:
            self.movePoint(self.index,self.type,self.mouse_x,self.mouse_y)

    def sceneMouseDoubleClick(self, ev):
        if ev.buttons() == Qt.MouseButton.LeftButton:
            index,type = self.mouseChecker(self.mouse_x,self.mouse_y)
            if type is not None:
                self.deletePoint(type,index)
            else:
                self.addPoint(self.mouse_x,self.mouse_y)
            return

        if ev.buttons() == Qt.MouseButton.RightButton:
            self.index,self.type = self.mouseChecker(self.mouse_x,self.mouse_y)
            if self.type is not None:
                if self.points[self.index].v is None:
                    self.points[self.index].v = [self.mouse_x-self.points[self.index].p[0], self.mouse_y-self.points[self.index].p[1]]
                    self.type = SelectionType.VEL
                elif self.points[self.index].a is None:
                    self.points[self.index].a = [self.mouse_x-self.points[self.index].p[0], self.mouse_y-self.points[self.index].p[1]]
                    self.type = SelectionType.ACC
                self.refresh()
                self.graph.setMouseEnabled(False,False)

    def sceneMousePress(self, ev):
        if ev.buttons() == Qt.MouseButton.LeftButton:
            self.index,self.type = self.mouseChecker(self.mouse_x,self.mouse_y)
            if self.type is not None:
                self.graph.setMouseEnabled(False,False)
            

    def sceneMouseRelease(self, ev):
        if self.type is not None:
            self.graph.setMouseEnabled(True,True)
            self.type = self.index = None


    def rangeUpdate(self,ev):
        range = self.graph.visibleRange()
        xdiff = range.right() - range.left()
        self.click_scale = abs(xdiff * 0.01)
        
    def clear(self):
        #Graph Data
        self.points.clear()
        self.interpolant = [],[]
        self.sample= [],[]

        #Plot Data
        self.point_scatter.clear()
        self.vel_scatter.clear()
        self.acc_scatter.clear()
        self.vel_vector.clear()
        self.acc_vector.clear()
        self.curve_plot.clear()

        #Coords
        for coords in self.coords:
            coords.setVisible(False)

        #Refresh graph
        self.graph.scene().update()

    def mouseChecker(self, x,y):
        min_dis = self.click_scale
        for i, point in enumerate(self.points):
            dis = np.linalg.norm(np.array([x-point.p[0], y-point.p[1]]))
            if (dis < min_dis):
                return i,SelectionType.POINT
            
            if (point.v is not None):
                dis = np.linalg.norm(np.array([x- (point.p[0] + point.v[0]), y-(point.p[1]+point.v[1])]))
                if (dis < min_dis):
                    return i,SelectionType.VEL
            
            if (point.a is not None):
                dis = np.linalg.norm(np.array([x- (point.p[0] + point.a[0]), y-(point.p[1]+point.a[1])]))
                if (dis < min_dis):
                    return i,SelectionType.ACC
        
        return None,None

    def addPoint(self,px,py,vx=None,vy=None,ax=None,ay=None,m=1):
        
        index = len(self.points)

        if index >= 10:
            return

        xmax = px+5
        xmin = px-5
        ymax = py+5
        ymin = py-5

        calc_index = index*3
        self.coords[calc_index].setText("[p%i,x:%0.2f,y:%0.2f,m:%0.2f]" % (index,px,py,m))
        self.coords[calc_index].setPos(px,py)
        self.coords[calc_index].setVisible(True)

        if vx is not None:
            vx = clamp(px+vx, xmin,xmax)-px
            vy = clamp(px+vy, ymin,ymax)-py

            self.coords[calc_index+1].setText("[v%i,x:%0.2f,y:%0.2f]" % (index,vx,vy))
            self.coords[calc_index+1].setPos(px+vx, py+vy)
            self.coords[calc_index+1].setVisible(True)
        if ax is not None:
            ax = clamp(px+ax, xmin,xmax)-px
            ay = clamp(py+ay, ymin,ymax)-py

            self.coords[calc_index+2].setText("[a%i,x:%0.2f,y:%0.2f]" % (index,ax,ay))
            self.coords[calc_index+2].setPos(px+ax, py+ay)
            self.coords[calc_index+2].setVisible(True)
        self.points.append(Point(px,py,vx,vy,ax,ay,m))

        object = PointDetails(index,px,py,m)
        self.points_ui.addWidget(object)

        self.updateData()
        self.graph.scene().update()

    def deletePoint(self, type,index):
        if type == SelectionType.POINT:
            self.points.pop(index)
        elif type == SelectionType.VEL and self.points[index].a is None:
            self.points[index].v = None
            self.points[index].a = None
        elif type == SelectionType.ACC:
            self.points[index].a = None

        for coord in self.coords:
            coord.setVisible(False)

        self.refresh()

    def movePoint(self, index, type, x,y):
        xmax = self.points[index].p[0]+5
        xmin = self.points[index].p[0]-5
        ymax = self.points[index].p[1]+5
        ymin = self.points[index].p[1]-5
        nx=clamp(x,xmin,xmax)
        ny=clamp(y,ymin,ymax)
        if type == SelectionType.POINT:
            self.points[index].p[0] = x
            self.points[index].p[1] = y
        elif type == SelectionType.VEL:
            self.points[index].v[0] = nx - self.points[index].p[0]
            self.points[index].v[1] = ny -self.points[index].p[1]
        elif type == SelectionType.ACC:
            self.points[index].a[0] = nx - self.points[index].p[0]
            self.points[index].a[1] = ny -self.points[index].p[1]
        
        self.refresh()

    def refresh(self):
        for index, point in enumerate(self.points):
            calc_index = index*3
            self.coords[calc_index].setText("[p%i,x:%0.2f,y:%0.2f,m:%0.2f]" % (index,point.p[0],point.p[1],point.m))
            self.coords[calc_index].setPos(point.p[0],point.p[1])
            self.coords[calc_index].setVisible(True)

            if point.v is not None:
                self.coords[calc_index+1].setText("[v%i,x:%0.2f,y:%0.2f]" % (index,point.v[0],point.v[1]))
                self.coords[calc_index+1].setPos(point.p[0]+point.v[0], point.p[1]+point.v[1])
                self.coords[calc_index+1].setVisible(True)
            
            if point.a is not None:
                self.coords[calc_index+2].setText("[a%i,x:%0.2f,y:%0.2f]" % (index,point.a[0],point.a[1]))
                self.coords[calc_index+2].setPos(point.p[0]+point.a[0], point.p[1]+point.a[1])
                self.coords[calc_index+2].setVisible(True)

        self.updateData()
        self.graph.scene().update()

    def updateData(self):
        p = [],[]
        vel = [],[]
        acc = [],[]

        vel_vec =[],[]
        vel_vec_con = []

        acc_vec =[],[]
        acc_vec_con = []

        self.interpolant = [],[]

        for point in self.points:
            p[0].append(point.p[0])
            p[1].append(point.p[1])
            self.interpolant[0].append(point.p[0])
            self.interpolant[1].append(point.p[1])

            if point.v is not None:
                vel[0].append(point.p[0]+point.v[0])
                vel[1].append(point.p[1]+point.v[1])
                vel_vec[0].append(point.p[0])
                vel_vec[0].append(point.p[0]+point.v[0])
                vel_vec[1].append(point.p[1])
                vel_vec[1].append(point.p[1]+point.v[1])
                vel_vec_con.append(1);
                vel_vec_con.append(0);
                self.interpolant[0].append(point.v[0])
                self.interpolant[1].append(point.v[1])
                
            
            if point.a is not None:
                acc[0].append(point.p[0]+point.a[0])
                acc[1].append(point.p[1]+point.a[1])
                acc_vec[0].append(point.p[0])
                acc_vec[0].append(point.p[0]+point.a[0])
                acc_vec[1].append(point.p[1])
                acc_vec[1].append(point.p[1]+point.a[1])
                acc_vec_con.append(1);
                acc_vec_con.append(0);
                self.interpolant[0].append(point.a[0])
                self.interpolant[1].append(point.a[1])
                
        self.point_scatter.setData(p[0], p[1])
        self.vel_scatter.setData(vel[0],vel[1])
        self.acc_scatter.setData(acc[0],acc[1])
        self.vel_vector.setData(vel_vec[0],vel_vec[1],connect=np.array(vel_vec_con))
        self.acc_vector.setData(acc_vec[0],acc_vec[1],connect=np.array(acc_vec_con))
        self.updateCurve()

    def updateCurve(self):
        # Calculate divided difference table
        # Reset
        gx = []
        gy = []

        # Stage 0
        if len(self.interpolant[0]) > 0:
            gx.append(self.interpolant[0])
            gy.append(self.interpolant[1])
        # Other stages
        for i in range(len(self.interpolant[0]) - 1):
            temp_x = []
            temp_y = []
            
            for j in range(len(gx[i]) - 1):
                temp_x.append((gx[i][j+1] - gx[i][j]) / (i+1+j - j))
                temp_y.append((gy[i][j+1] - gy[i][j]) / (i+1+j - j))
            gx.append(temp_x)
            gy.append(temp_y)
        
        # Calculate the polynomial using newton form

        px = NewtonFrom(gx)
        py = NewtonFrom(gy)
        t = np.linspace(0, len(px) - 1, num = 500)
        self.sample_x = []
        self.sample_y = []
        for i in range(len(t)):
            self.sample_x.append(PolyValue(t[i],px))
            self.sample_y.append(PolyValue(t[i],py))

        self.curve_plot.setData(self.sample_x, self.sample_y)
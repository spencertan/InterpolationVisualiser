from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QSlider
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

def GenerateLayout(orientation, alignment = 0,left=0,top=0,right=0,bottom=0,spacing=0,):
    layout = QVBoxLayout() if orientation == Qt.Vertical else QHBoxLayout()
    layout.setContentsMargins(left,top,right,bottom)
    layout.setSpacing(spacing)
    layout.setAlignment(alignment)
    return layout

def GenerateLabel(string="",alignment=0, font = None,min_size=None,max_size=None):
    label = QLabel(string)
    label.setAlignment(alignment)
    label.setFont(font)
    if min_size is not None: label.setMinimumSize(min_size[0],min_size[1])
    if max_size is not None: label.setMaximumSize(max_size[0],max_size[1])
    return label

def GenerateDoubleSlider(orientation, decimal,value=None, min=0, max=0, step=0.1,min_size=None,max_size=None):
    slider = DoubleSlider(decimal,orientation)
    slider.setMinimum(min)
    slider.setMaximum(max)
    slider.setSingleStep(step)
    slider.setValue(value if value is not None else 0)
    if min_size is not None: slider.setMinimumSize(min_size[0],min_size[1])
    if max_size is not None: slider.setMaximumSize(max_size[0],max_size[1])
    return slider

def GenerateFrame(orientation,alignment,left,top,right,bottom,spacing):
    frame = QFrame()
    layout = GenerateLayout(orientation,alignment,left,top,right,bottom,spacing)
    frame.setLayout(layout)
    return frame

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    sigDoubleValueChanged = Signal(float)

    def __init__(self, decimals=3, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.doubleValueChanged)

    def doubleValueChanged(self):
        value = float(super(DoubleSlider, self).value())/self._multi
        self.sigDoubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))

class PointDetails(QFrame):
  def __init__(self, index, px,py,m,vx=None,vy=None,ax=None,ay=None):
    super().__init__()

    header_font=QFont()
    header_font.setBold(True)
    header_font.setPointSize(12)

    body_font = QFont()
    body_font.setBold(True)
    body_font.setPointSize(9)


    self.mass_value_label = None
    self.mass_slider = None
    self.mass_value = m

    self.coord_value_label = None
    self.coord_slider = [None,None]
    self.coord_value = [px,py]

    self.vel_value_label = None
    self.vel_slider = [None,None]
    self.vel_value = [vx,vy]

    self.acc_value_label = None
    self.acc_slider = [None,None]
    self.acc_value = [ax,ay]

    label_max = label_min = (50,16777215)
    
    value_label_max = value_label_min = (90,16777215)

    #layout
    layout = GenerateLayout(Qt.Vertical,Qt.AlignTop,4,4,4,4,4,)
    self.setLayout(layout)
    self.name_label = GenerateLabel("Point (%i)"%index, Qt.AlignLeft, header_font)
    layout.addWidget(self.name_label)


    #Mass
    mass_frame = GenerateFrame(Qt.Horizontal,Qt.AlignLeft,4,4,4,4,4)
    layout.addWidget(mass_frame)
    mass_label = GenerateLabel("Mass:", Qt.AlignLeft, body_font,min_size=label_min,max_size=label_max)
    self.mass_value_label = GenerateLabel("(%.2f)"%m, Qt.AlignLeft,body_font,min_size=value_label_min,max_size=value_label_max)
    self.mass_slider = GenerateDoubleSlider(Qt.Horizontal,3,m,-1.0,1.0,0.1)
    self.mass_slider.setValue(m)
    mass_frame.layout().addWidget(mass_label)
    mass_frame.layout().addWidget(self.mass_value_label)
    mass_frame.layout().addWidget(self.mass_slider)
    

    #Point
    coord_frame = GenerateFrame(Qt.Horizontal,Qt.AlignLeft,4,4,4,4,4)
    layout.addWidget(coord_frame)
    point_label = GenerateLabel("Coord:", Qt.AlignLeft, body_font,min_size=label_min,max_size=label_max)
    self.coord_value_label = GenerateLabel("(%.2f,%.2f)"%(px,py), Qt.AlignLeft,body_font,min_size=value_label_min,max_size=value_label_max)
    self.coord_slider[0] = GenerateDoubleSlider(Qt.Horizontal,3,px,-100.0,100.0,0.1)
    self.coord_slider[1] = GenerateDoubleSlider(Qt.Horizontal,3,py,-100.0,100.0,0.1)
    coord_frame.layout().addWidget(point_label)
    coord_frame.layout().addWidget(self.coord_value_label)
    coord_frame.layout().addWidget(self.coord_slider[0])
    coord_frame.layout().addWidget(self.coord_slider[1])
    self.coord_slider[0].setValue(px)
    self.coord_slider[1].setValue(py)

    #Vel
    vel_frame = GenerateFrame(Qt.Horizontal,Qt.AlignLeft,4,4,4,4,4)
    layout.addWidget(vel_frame)
    vel_label = GenerateLabel("Velocity:", Qt.AlignLeft, body_font,min_size=label_min,max_size=label_max)
    self.vel_value_label = GenerateLabel("(%.2f,%.2f)"%(vx,vy) if vx is not None else "", Qt.AlignLeft,body_font,min_size=value_label_min,max_size=value_label_max)
    self.vel_slider[0] = GenerateDoubleSlider(Qt.Horizontal,3,vx,-10.0,10.0,0.1)
    self.vel_slider[1] = GenerateDoubleSlider(Qt.Horizontal,3,vy,-10.0,10.0,0.1)
    vel_frame.layout().addWidget(vel_label)
    vel_frame.layout().addWidget(self.vel_value_label)
    vel_frame.layout().addWidget(self.vel_slider[0])
    vel_frame.layout().addWidget(self.vel_slider[1])
    if vx is not None:
        self.vel_slider[0].setValue(vx)
        self.vel_slider[1].setValue(vy)


    #Acc
    acc_frame = GenerateFrame(Qt.Horizontal,Qt.AlignLeft,4,4,4,4,4)
    layout.addWidget(acc_frame)
    acc_label = GenerateLabel("Acceleration:", Qt.AlignLeft, body_font,min_size=label_min,max_size=label_max)
    self.acc_value_label = GenerateLabel("(%.2f,%.2f)"%(ax,ay) if ax is not None else "", Qt.AlignLeft,body_font,min_size=value_label_min,max_size=value_label_max)
    self.acc_slider[0] = GenerateDoubleSlider(Qt.Horizontal,3,ax,-10.0,10.0,0.1)
    self.acc_slider[1] = GenerateDoubleSlider(Qt.Horizontal,3,ay,-10.0,10.0,0.1)
    acc_frame.layout().addWidget(acc_label)
    acc_frame.layout().addWidget(self.acc_value_label)
    acc_frame.layout().addWidget(self.acc_slider[0])
    acc_frame.layout().addWidget(self.acc_slider[1])
    if ax is not None:
        self.acc_slider[0].setValue(vx)
        self.acc_slider[1].setValue(vy)

    layout.addWidget(QHLine())
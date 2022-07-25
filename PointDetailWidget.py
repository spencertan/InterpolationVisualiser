from cmath import isclose, isinf
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap


def GenerateLayout(
    orientation,
    alignment=0,
    left=0,
    top=0,
    right=0,
    bottom=0,
    spacing=0,
):
    layout = QVBoxLayout() if orientation == Qt.Vertical else QHBoxLayout()
    layout.setContentsMargins(left, top, right, bottom)
    layout.setSpacing(spacing)
    layout.setAlignment(alignment)
    return layout


def GenerateLabel(string="", alignment=0, font=None, min_size=None, max_size=None):
    label = QLabel(string)
    label.setAlignment(alignment)
    label.setFont(font)
    if min_size is not None:
        label.setMinimumSize(min_size[0], min_size[1])
    if max_size is not None:
        label.setMaximumSize(max_size[0], max_size[1])
    return label


def GenerateDoubleSlider(
    orientation,
    decimal,
    value=None,
    min=0,
    max=0,
    step=0.1,
    min_size=None,
    max_size=None,
):
    slider = DoubleSlider(decimal, orientation)
    slider.setMinimum(min)
    slider.setMaximum(max)
    slider.setSingleStep(step)
    slider.setValue(value if value is not None else 0)
    if min_size is not None:
        slider.setMinimumSize(min_size[0], min_size[1])
    if max_size is not None:
        slider.setMaximumSize(max_size[0], max_size[1])
    return slider


def GenerateFrame(
    orientation, alignment=0, left=0, top=0, right=0, bottom=0, spacing=0
):
    frame = QFrame()
    layout = GenerateLayout(orientation, alignment, left, top, right, bottom, spacing)
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

    def __init__(self, decimals=1, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        self._multi = 10**decimals

        self.valueChanged.connect(self.doubleValueChanged)

    def doubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
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
        calc = value * self._multi
        v = 0 if isinf(calc) else calc
        super(DoubleSlider, self).setValue(v)


class PointDetails(QFrame):

    sigUpChange = Signal(int)
    sigDownChange = Signal(int)

    def __init__(self, index, px, py, m, vx=None, vy=None, ax=None, ay=None):
        super().__init__()

        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)

        body_font = QFont()
        body_font.setBold(True)
        body_font.setPointSize(9)

        self.index_value = index
        self.mass_value = m
        self.point_value = [px, py]
        self.vel_value = [vx, vy]
        self.acc_value = [ax, ay]

        # layout
        layout = GenerateLayout(
            Qt.Vertical,
            Qt.AlignTop,
            4,
            4,
            4,
            4,
            4,
        )

        # Setup
        self.setLayout(layout)
        self.point_frame = GenerateFrame(Qt.Horizontal, Qt.AlignLeft, 4, 4, 4, 4, 4)
        layout.addWidget(self.point_frame)
        self.name_label = GenerateLabel("Point (%i)" % index, Qt.AlignLeft, header_font)
        self.uparrow = QPushButton()
        self.uparrow.setMaximumSize(QSize(16, 16))
        self.uparrow.setText("")
        up_icon = QIcon()
        up_icon.addPixmap(
            QPixmap("UI\\arrow-up.svg"), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.uparrow.setIcon(up_icon)
        self.uparrow.setIconSize(QSize(16, 16))
        self.uparrow.setObjectName("uparrow")
        self.uparrow.clicked.connect(lambda: self.sigUpChange.emit(self.index_value))

        self.downarrow = QPushButton()
        self.downarrow.setMaximumSize(QSize(16, 16))
        self.downarrow.setText("")
        down_icon = QIcon()
        down_icon.addPixmap(
            QPixmap("UI\\arrow-down.svg"), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.downarrow.setIcon(down_icon)
        self.downarrow.setIconSize(QSize(16, 16))
        self.downarrow.setObjectName("downarrow")
        self.downarrow.clicked.connect(
            lambda: self.sigDownChange.emit(self.index_value)
        )

        self.point_frame.layout().addWidget(self.name_label)
        self.point_frame.layout().addWidget(self.uparrow)
        self.point_frame.layout().addWidget(self.downarrow)

        # Mass
        """
      *mass_frame(Mass Wrapper)
          *mass_label(Value Label)
          *mass_slider_frame(Slider Frame)
              mass_slider_label(Slider Label)
              *mass_slider(Slider)
      """
        self.mass_frame = GenerateFrame(Qt.Vertical, Qt.AlignLeft, 4, 4, 4, 4, 4)
        layout.addWidget(self.mass_frame)
        self.mass_label = GenerateLabel("Mass: (%.2f)" % m, Qt.AlignLeft, body_font)

        self.mass_slider_frame = GenerateFrame(Qt.Horizontal, Qt.AlignLeft)

        mass_slider_label = GenerateLabel("m ", Qt.AlignLeft, body_font)
        self.mass_slider = GenerateDoubleSlider(Qt.Horizontal, 1, m, -1.0, 1.0, 0.1)

        self.mass_slider.sigDoubleValueChanged.connect(self.massSliderUpdate)

        self.mass_slider_frame.layout().addWidget(mass_slider_label)
        self.mass_slider_frame.layout().addWidget(self.mass_slider)
        self.mass_frame.layout().addWidget(self.mass_label)
        self.mass_frame.layout().addWidget(self.mass_slider_frame)

        # Point
        """
      *point_frame(Mass Wrapper)
          *point_label(Value Label)
          *point_slider_frame[0](Slider Frame)
              x_slider_label(Slider Label)
              *point_slider[0](Slider)
          *slider_frame[1](Slider Frame)
              y_slider_label(Slider Label)
              *point_slider[1](Slider)
      """
        self.point_frame = GenerateFrame(Qt.Vertical, Qt.AlignLeft, 4, 4, 4, 4, 4)
        layout.addWidget(self.point_frame)
        self.point_label = GenerateLabel(
            "Coord: (%.2f,%.2f)" % (px, py), Qt.AlignLeft, body_font
        )

        self.point_slider_frame = [
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
        ]

        x_slider_label = GenerateLabel("x ", Qt.AlignLeft, body_font)
        y_slider_label = GenerateLabel("y ", Qt.AlignLeft, body_font)
        self.point_slider = [
            GenerateDoubleSlider(Qt.Horizontal, 1, px, -50.0, 50.0, 0.1),
            GenerateDoubleSlider(Qt.Horizontal, 1, py, -50.0, 50.0, 0.1),
        ]

        self.point_slider[0].sigDoubleValueChanged.connect(
            lambda f: self.pointSliderUpdate(0, f)
        )
        self.point_slider[1].sigDoubleValueChanged.connect(
            lambda f: self.pointSliderUpdate(1, f)
        )

        self.point_slider_frame[0].layout().addWidget(x_slider_label)
        self.point_slider_frame[0].layout().addWidget(self.point_slider[0])
        self.point_slider_frame[1].layout().addWidget(y_slider_label)
        self.point_slider_frame[1].layout().addWidget(self.point_slider[1])

        self.point_frame.layout().addWidget(self.point_label)
        self.point_frame.layout().addWidget(self.point_slider_frame[0])
        self.point_frame.layout().addWidget(self.point_slider_frame[1])

        # Vel
        """
      *vel_frame(Mass Wrapper)
          *vel_label(Value Label)
          *vel_slider_frame[0](Slider Frame)
              vel_x_slider_label(Slider Label)
              *vel_slider[0](Slider)
          *vel_slider_frame[1](Slider Frame)
              vel_y_slider_label(Slider Label)
              *vel_slider[1](Slider)
      """
        self.vel_frame = GenerateFrame(Qt.Vertical, Qt.AlignLeft, 4, 4, 4, 4, 4)
        layout.addWidget(self.vel_frame)
        self.vel_label = GenerateLabel(
            "Velocity: (%.2f,%.2f)" % (vx, vy) if vx is not None else "Velocity: (-,-)",
            Qt.AlignLeft,
            body_font,
        )

        self.vel_slider_frame = [
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
        ]

        vel_x_slider_label = GenerateLabel("x ", Qt.AlignLeft, body_font)
        vel_y_slider_label = GenerateLabel("y ", Qt.AlignLeft, body_font)
        self.vel_slider = [
            GenerateDoubleSlider(Qt.Horizontal, 1, vx, -5.0, 5.0, 0.1),
            GenerateDoubleSlider(Qt.Horizontal, 1, vy, -5.0, 5.0, 0.1),
        ]

        self.vel_slider[0].sigDoubleValueChanged.connect(
            lambda f: self.velSliderUpdate(0, f)
        )
        self.vel_slider[1].sigDoubleValueChanged.connect(
            lambda f: self.velSliderUpdate(1, f)
        )

        self.vel_slider_frame[0].layout().addWidget(vel_x_slider_label)
        self.vel_slider_frame[0].layout().addWidget(self.vel_slider[0])
        self.vel_slider_frame[1].layout().addWidget(vel_y_slider_label)
        self.vel_slider_frame[1].layout().addWidget(self.vel_slider[1])

        self.vel_frame.layout().addWidget(self.vel_label)
        self.vel_frame.layout().addWidget(self.vel_slider_frame[0])
        self.vel_frame.layout().addWidget(self.vel_slider_frame[1])

        if vx is None:
            self.vel_frame.setVisible(True)

        # Acc
        """
      *acc_frame(Mass Wrapper)
          *acc_label(Value Label)
          *acc_slider_frame[0](Slider Frame)
              acc_x_slider_label(Slider Label)
              *acc_slider[0](Slider)
          *acc_slider_frame[1](Slider Frame)
              acc_y_slider_label(Slider Label)
              *acc_slider[1](Slider)
      """
        self.acc_frame = GenerateFrame(Qt.Vertical, Qt.AlignLeft, 4, 4, 4, 4, 4)
        layout.addWidget(self.acc_frame)
        self.acc_label = GenerateLabel(
            "Acceleration: (%.2f,%.2f)" % (ax, ay)
            if ax is not None
            else "Acceleration: (-,-)",
            Qt.AlignLeft,
            body_font,
        )

        self.acc_slider_frame = [
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
            GenerateFrame(Qt.Horizontal, Qt.AlignLeft),
        ]

        acc_x_slider_label = GenerateLabel("x ", Qt.AlignLeft, body_font)
        acc_y_slider_label = GenerateLabel("y ", Qt.AlignLeft, body_font)
        self.acc_slider = [
            GenerateDoubleSlider(Qt.Horizontal, 1, ax, -5.0, 5.0, 0.1),
            GenerateDoubleSlider(Qt.Horizontal, 1, ay, -5.0, 5.0, 0.1),
        ]

        self.acc_slider[0].sigDoubleValueChanged.connect(
            lambda f: self.accSliderUpdate(0, f)
        )
        self.acc_slider[1].sigDoubleValueChanged.connect(
            lambda f: self.accSliderUpdate(1, f)
        )

        self.acc_slider_frame[0].layout().addWidget(acc_x_slider_label)
        self.acc_slider_frame[0].layout().addWidget(self.acc_slider[0])
        self.acc_slider_frame[1].layout().addWidget(acc_y_slider_label)
        self.acc_slider_frame[1].layout().addWidget(self.acc_slider[1])

        self.acc_frame.layout().addWidget(self.acc_label)
        self.acc_frame.layout().addWidget(self.acc_slider_frame[0])
        self.acc_frame.layout().addWidget(self.acc_slider_frame[1])

        if ax is None:
            self.acc_frame.setVisible(True)

        layout.addWidget(QHLine())

    def indexValueUpdate(self, v):
        self.index_value = v
        self.name_label.setText("Point (%i)" % self.index_value)

    def massValueUpdate(self, v):
        self.mass_slider.setValue(v)

    def massSliderUpdate(self, f):
        increasing = True if f > self.mass_value else False
        if isclose(f, 0.0):
            self.mass_value = 0.01 if increasing else -0.01
        else:
            self.mass_value = f
        self.mass_label.setText("Mass: (%.2f)" % self.mass_value)

    def pointValueUpdate(self, type, v):
        self.point_slider[type].setValue(v)

    def pointSliderUpdate(self, type, f):
        self.point_value[type] = f
        self.point_label.setText(
            "Coord: (%.2f,%.2f)" % (self.point_value[0], self.point_value[1])
        )

    def velValueUpdate(self, type, v):
        if v is None:
            self.vel_slider[0].setValue(0)
            self.vel_slider[1].setValue(0)
            self.vel_label.setText("Velocity: (-,-)")
        elif v <= 5.0 and v >= -5.0:
            self.vel_slider[type].setValue(v)

    def velSliderUpdate(self, type, f):
        if type == 0:
            self.vel_value[0] = f
            if self.vel_value[1] is None:
                self.vel_value[1] = 0.0
        else:
            self.vel_value[1] = f
            if self.vel_value[0] is None:
                self.vel_value[0] = 0.0

        if self.vel_value[0] is not None:
            text = "Velocity: (%.2f,%.2f)" % (self.vel_value[0], self.vel_value[1])
        else:
            text = "Velocity: (-,-)"
        self.vel_label.setText(text)

    def accValueUpdate(self, type, v):
        if v is None:
            self.acc_slider[0].setValue(0)
            self.acc_slider[1].setValue(0)
            self.acc_label.setText("Acceleration: (-,-)")
        elif v <= 5.0 and v >= -5.0:
            self.acc_slider[type].setValue(v)

    def accSliderUpdate(self, type, f):
        if type == 0:
            self.acc_value[0] = f
            if self.acc_value[1] is None:
                self.acc_value[1] = 0.0
        else:
            self.acc_value[1] = f
            if self.acc_value[0] is None:
                self.acc_value[0] = 0.0

        if self.acc_value[0] is not None:
            text = "Acceleration: (%.2f,%.2f)" % (self.acc_value[0], self.acc_value[1])
        else:
            text = "Acceleration: (-,-)"

        self.acc_label.setText(text)

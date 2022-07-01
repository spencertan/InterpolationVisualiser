## InterpolationVisualiser

![SS1](img/ss1.PNG?raw=true "SS1")

![SS2](img/ss2.PNG?raw=true "SS2")

An interpolation project written in Python using PyQT6 and PyQTGraph for visualisation with the goal of visualising the various interpolation techniques in Projective Grassmanian Space upto 2nd derivative if the technique supports it.

The project is also a first attempt to learn PyQT6, will be refining the GUI as I explore more of the framework.

**Note:The points details panel is not hooked up yet, so the controls does not work.

**The project aims to explore**
- Lagrange Interpolation
- Hermite Interpolation
- Newton Interpolation (Currently set-up with this, have to review and fix 1st and 2nd derivative)
- Bezier Interpolation

## Controls
- Double click on graph: Add point
- Double click on point: Delete point
- Double right-click on point and drag: Add 1st or 2nd derivative and move
- Single click on point and drag: Move point
- Single click on graph and drag: Move the graph
- Single Right click on graph and drag: Scale the graph
- Mousewheel: Zoom in and out of graph

## Tools
- Top right folder icon: Load file
```
File format:
[x] [y]                         ## Point information
[x] [y] [m]                     ## Point, mass information
[x] [y] [vx] [vy]               ## Point, 1st derivative information
[x] [y] [vx] [vy] [m]           ## Point, 1st derivative, mass information
[x] [y] [vx] [vy] [ax] [ay]     ## Point, 1st and 2nd derivative information
[x] [y] [vx] [vy] [ax] [ay] [m] ## Point, 1st and 2nd derivative, mass information

```
- Top right file icon: New graph
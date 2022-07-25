from itertools import zip_longest

def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))

def PolyMultiply(p1, p2):
    result_coeffs = [0] * (len(p1) + len(p2) - 1)
    for index1, coeff1 in enumerate(p1):
        for index2, coeff2 in enumerate(p2):
            result_coeffs[index1 + index2] += coeff1 * coeff2
    return result_coeffs

def PolyAdd(p1, p2):
    return [a + b for a, b in zip_longest(p1, p2, fillvalue=0)]

def PolyScale(p, s):
    for i in range(len(p)):
        p[i] *= s
    return p

def PolyValue(x, coeffs):
    d = len(coeffs)
    y = 0
    for i in range(d):
        y += coeffs[i] * x ** i
    return y

def NewtonFrom(g):
    p = []
    #test = []
    for i in range(len(g)):
        temp = [1]
        for j in range(i):
            temp = PolyMultiply(temp, [-j, 1])
        p = PolyAdd(p, PolyScale(temp, g[i][0]))
        #test.append(p[i])
        #print("p value: ", p[i], ", i value: ", i)
    #print("p",p)
    #return test
    return p

"""
Bezier Interpolation:
Binomial - Build binomial term for Bezier and RationalBezier
Bezier - Build Bezier Curve using bernstein
RationalBezier - Build Rational Bezier Curve using bernstein

DeCasteljau - Build Bezier Curve using using DeCasteljau
RationalDeCasteljau - Build Bezier Curve using DeCasteljau
"""

tri = [      [1],                          #n=0
            [1,1],                         #n=1
           [1,2,1],                        #n=2
          [1,3,3,1],                       #n=3
         [1,4,6,4,1],                      #n=4
        [1,5,10,10,5,1],                   #n=5
       [1,6,15,20,15,6,1],                 #n=6
      [1,7,21,35,35,21,7,1],               #n=7
     [1,8,28,56,70,56,28,8,1],             #n=8
    [1,9,36,84,126,126,84,36,9,1],         #n=9
   [1,10,45,120,210,252,210,120,45,10,1]]  #n=10

def Binomial(n:int, k:int):
    while (n >= len(tri)):
        size = len(tri)
        next_row = [1]
        for i in range(1,size):
            prev = size - 1
            next_row.append(tri[prev][i-1] + tri[prev][i])
        next_row.append(1)
        tri.append(next_row)
    return tri[n][k]

def Bezier(px:list,py:list,t:float):
    n = len(px)-1
    sum_x = sum_y = 0
    for k in range(n+1):
        func = Binomial(n,k) * (1-t)**(n-k) * t**k
        sum_x += px[k] * func
        sum_y += py[k] * func
    return sum_x,sum_y

def RationalBezier(px:list,py:list,m:list,t:float):
    n = len(px)-1
    sum_x = 0.0
    sum_y = 0.0
    basis = 0.0

    for k in range(n+1):
        func = m[k] * Binomial(n,k) * (1-t)**(n-k) * t**k
        basis += func
        sum_x += px[k] * func
        sum_y += py[k] * func
    return sum_x/basis, sum_y/basis 

def DeCasteljau(rx:list,ry:list,px:list,py:list,t:float):
  if len(px) == 1:
    rx.append(px[0])
    ry.append(py[0])
  else:
    for i in range(len(px)-1):
        px[i] = (1-t) * px[i] + t * px[i+1]
        py[i] = (1-t) * py[i] + t * py[i+1]
    del px[-1]
    del py[-1]
    DeCasteljau(rx,ry,px,py,t)

def RationalDeCasteljau(rx:list,ry:list,px:list,py:list,m:list,t:float):
  if len(px) == 1:
    rx.append(px[0])
    ry.append(py[0])
  else:
    for i in range(len(px)-1):
        tm = (1-t) * m[i] + t *m[i+1]
        px[i] = ((1-t) * px[i] * m[i] + t * px[i+1] * m[i+1]) / tm
        py[i] = ((1-t) * py[i] * m[i] + t * py[i+1] * m[i+1]) / tm
        m[i] = tm
    del px[-1]
    del py[-1]
    del m[-1]
    RationalDeCasteljau(rx,ry,px,py,m,t)

def GenerateVelocity(px,py,cx,cy):
    return 3*(cx-px), 3*(cy-py)

def GenerateAcceleration(px,py,cx,cy,cxx,cyy):
    return 6*(cxx - 2*cx + px), 6*(cyy-2*cy-py)

def GenerateC1C2(vx,vy,ax,ay,px,py):
    cx = vx/3 + px
    cy = vy/3 + py
    cxx = ax/6 + ((2*vx)/3) + px
    cyy = ay/6 + ((2*vy)/3) + py
    return cx,cy,cxx,cyy

def GeneratePoints(rx,ry,rm,px,py,m,vx,vy,ax,ay):
    for i in range(len(px)):
        rx.append(px[i])
        ry.append(py[i])
        rm.append(m[i])

        if i == len(px) - 1:
            return

        c0x,c0y,c1x,c1y = GenerateC1C2(vx[i],vy[i],ax[i],ay[i],px[i],py[i])
        rx.append(c0x)
        rx.append(c1x)
        ry.append(c0y)
        ry.append(c1y)
        rm.append(m[i])
        rm.append(m[i])

def GenerateVelocityAccelerations(rvx,rvy,rax,ray,px,py,vx,vy,ax,ay):

  pvx = pvy = 0
  pax = pay = 0
  for i in range(len(px)):
    rvx.append(vx)
    rvy.append(vy)
    rax.append(ax)
    ray.append(ay)
    
    if i == len(px) - 1:
      return

    c0x,c0y,c1x,c1y = GenerateC1C2(vx,vy,ax,ay,px[i],py[i])
    pvx = vx
    pvy = vy
    pax = ax
    pay = ay
    vx,vy = GenerateVelocity(c1x,c1y,px[i+1],py[i+1])
    ax,ay = GenerateAcceleration(c0x,c0y,c1x,c1y,px[i+1], py[i+1])

    vx = (vx / pvx) if pvx >0 else vx
    vy = (vy / pvy) if pvy >0 else vy
    ax = (ax / pax) if pax >0 else ax
    ay = (ay / pay) if pay >0 else ay
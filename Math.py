from itertools import zip_longest

def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))

def PolyMultiply(p1, p2):
    result_coeffs = [0] * (len(p1) + len(p2) - 1)
    for i, c1 in enumerate(p1):
        for j, c2 in enumerate(p2):
            result_coeffs[i + j] += c1 * c2
    return result_coeffs

def PolyAdd(p1, p2):
    return [a + b for a, b in zip_longest(p1, p2, fillvalue=0)]

def PolyScale(p, s):
    for i in range(len(p)): p[i] *= s
    return p

def PolyValue(x, coeffs):
    d = len(coeffs)
    y = 0
    for i in range(d): y += coeffs[i] * x ** i
    return y

def NewtonFrom(g):
    p = []
    for i in range(len(g)):
        temp = [1]
        for j in range(i): temp = PolyMultiply(temp, [-j, 1])
        p = PolyAdd(p, PolyScale(temp, g[i][0]))
    return p
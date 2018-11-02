from cvxopt import matrix, solvers
import numpy as np
import cvxopt

'''
问题描述：
minimize xQx+px
subject Gx <= h
        Ax = b
注：Q=[[2, .5], [.5, 1]]，即xQx=2x1^2+x^2+x1*x2
'''

Q = 2*matrix(np.array([[2, .5], [.5, 1]]))  # 一定要乘以2
p = matrix([1.0, 1.0])
G = matrix([[-1.0, 0.0], [0.0, -1.0]])
h = matrix([0.0, 0.0])
A = matrix([1.0, 1.0], (1, 2))
b = matrix(1.0)

sol = solvers.qp(Q, p, G, h, A, b)
print(sol['x'], sol['y'])
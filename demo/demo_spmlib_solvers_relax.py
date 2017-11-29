# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 13:16:41 2017

@author: tsakai
"""

from math import sqrt
import numpy as np
from scipy import linalg
import scipy.sparse.linalg as splinalg

from time import time
import matplotlib.pyplot as plt

from spmlib import solver as sps

    

#x0 = rng.randn(3) + rng.randn(3)*1j
##print np.real(x0.conj().T.dot(x0))
#x = sgn(x0)
#print linalg.norm(x,1)


#%% Demo: Sparse solvers
rng = np.random.RandomState(int(time()))
#m, n = 512, 2048
#m, n = 1024, 8192
m, n = 2048, 8192

dtype = np.float32

# generate a k-sparse Gaussian signal vector
k = m//8
stdx = 1.
snr = 100. # try 10., 5.. and observe the bias

# use a random matrix as a basis (design matrix)
A = rng.randn(m, n).astype(dtype) / sqrt(m)  # random design

x_true = np.zeros(n, dtype=dtype)
T = np.random.permutation(n)[:k]
x_true[T] = rng.randn(k).astype(dtype) * stdx
#x_true[T] = rng.rand(k) * stdx
#x_true = rng.randn(n)
#x_true[abs(x_true) < 2.5] = 0  ## sparsify

# make the query vector
b_true = splinalg.aslinearoperator(A).matvec(x_true)

# add noise
normb = linalg.norm(b_true)
noise = rng.randn(m).astype(dtype)
noise = noise / linalg.norm(noise) * normb / snr
tol = linalg.norm(noise)
b = b_true + noise



plt.close('all')




import numpy as np
from scipy import linalg



#l = 0.1*stdx
l = (stdx*stdx / k * m) / sqrt(snr) / normb


# FISTA (naive use to obtain biased solution)
print("Running FISTA")
t0 = time()
result_FISTA = sps.fista(A, b, tol=tol, l=l, tolx=linalg.norm(A.T.dot(b))*1e-5, maxiter=1000)
x_est = result_FISTA[0]
print('done in %.2fs.' % (time() - t0))
print('# nonzeros = %d' % (np.count_nonzero(x_est)))
#print('supprt = ')
#print(np.nonzero(x_est)[0])
print('rel. error of x = %.2e' % (linalg.norm(x_est-x_true)/linalg.norm(x_true)))
print('rel. reconst. error = %.2e' % (linalg.norm(A.dot(x_est)-b_true)/normb))

plt.figure()
#plt.stem(x_true, markerfmt='g.')
plt.plot(np.arange(n), x_true, 'g.', markersize=8, mec='green', label='True')
plt.plot(np.arange(n), x_est, 'ro', mfc = 'None', markersize=8, mec='red', label='Estimated')
plt.legend(loc='upper right', shadow=False)
plt.show()



# FISTA followed by LS debias (a neat use)
print("Running FISTA as support estimation followed by nonzero estimation via LS debias..")
t0 = time()
result_FISTA_debias = sps.fista(A, b, tol=tol, l=l, tolx=linalg.norm(A.T.dot(b))*1e-5, maxiter=50, debias=True)
x_est = result_FISTA_debias[0]
print('done in %.2fs.' % (time() - t0))
print('# nonzeros = %d' % (np.count_nonzero(x_est)))
#print('supprt = ')
#print(np.nonzero(x_est)[0])
print('rel. error of x = %.2e' % (linalg.norm(x_est-x_true)/linalg.norm(x_true)))
print('rel. reconst. error = %.2e' % (linalg.norm(A.dot(x_est)-b_true)/normb))

plt.figure()
#plt.stem(x_true, markerfmt='g.')
plt.plot(np.arange(n), x_true, 'g.', markersize=8, mec='green', label='True')
plt.plot(np.arange(n), x_est, 'ro', mfc = 'None', markersize=8, mec='red', label='Estimated')
plt.legend(loc='upper right', shadow=False)
plt.show()



# FISTA with SCAD
print("Running FISTA with SCAD..")
t0 = time()
result_FISTA_SCAD = sps.fista_scad( A, b, tol=tol, switch_to_scad_after = 40,
                    l=l, maxiter=1000, tolx=linalg.norm(A.T.dot(b))*1e-5)
x_est = result_FISTA_SCAD[0]
print('done in %.2fs.' % (time() - t0))
print('# nonzeros = %d' % (np.count_nonzero(x_est)))
#print('supprt = ')
#print(np.nonzero(x_est)[0])
print('rel. error of x = %.2e' % (linalg.norm(x_est-x_true)/linalg.norm(x_true)))
print('rel. reconst. error = %.2e' % (linalg.norm(A.dot(x_est)-b_true)/normb))


plt.figure()
#plt.stem(x_true, markerfmt='g.')
plt.plot(np.arange(n), x_true, 'g.', markersize=8, mec='green', label='True')
plt.plot(np.arange(n), x_est, 'ro', mfc = 'None', markersize=8, mec='red', label='Estimated')
plt.legend(loc='upper right', shadow=False)
plt.show()



# If you have
# https://github.com/cvxopt/cvxopt/blob/master/examples/doc/chap8/l1regls.py
# and cvxopt installed, try the following code to make sure that
# FISTA is about ten times faster than the l1regls with CVXOPT for the same LASSO regression problem.
l1regls_cvxopt = False

if l1regls_cvxopt:
    from l1regls import l1regls
    from cvxopt import matrix
    A = matrix(A) / l
    b = matrix(b)

    print("Running l1regls")
    t0 = time()
    x_est = l1regls(A,b) / l
    print('done in %.2fs.' % (time() - t0))
    A = A * l
    print('# nonzeros = %d' % (np.count_nonzero(x_est)))
    #print('supprt = ')
    #print(np.nonzero(x_est)[0])
    print('rel. error of x = %.2e' % (linalg.norm(np.array(x_est).ravel()-x_true)/linalg.norm(x_true)))
    print('rel. reconst. error = %.2e' % (linalg.norm(np.array(A*x_est).ravel()-b_true)/normb))

    plt.figure()
    #plt.stem(x_true, markerfmt='g.')
    plt.plot(np.arange(n), x_true, 'g.', markersize=8, mec='green', label='True')
    plt.plot(np.arange(n), x_est, 'ro', mfc = 'None', markersize=8, mec='red', label='Estimated')
    plt.legend(loc='upper right', shadow=False)
    plt.show()



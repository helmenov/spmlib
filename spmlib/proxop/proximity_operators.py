# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 08:42:11 2017

@author: tsakai
"""

import numpy as np
from scipy import linalg
import scipy.sparse.linalg as splinalg
import spmlib.thresholding as th

# Proximity operators:
#     prox_(l*f())(q) = arg min_x  l * f(x) + (1./2.) || x - q ||_2^2
# Example:
# >>> from spmlib import proxop as prox


def ind_linfball(q, r, c=None):
    """
    prox of linf-ball with center c and radius r
    
    arg min_x ind_linfball(x,r,c) + 0.5*||x-q||_2^2 = q if q in the linf-ball, 
    otherwise q + soft(c-q, r)
    """
    if c is None:
        return q + th.soft(-q, r)
    else:
        return q + th.soft(c-q, r)



def ind_l2ball(q, r, c=None):
    """
    prox of l2-ball with center c and radius r
    
    arg min_x ind_l2ball(x,r,c) + 0.5*||x-q||_2^2 = q if q in the l2-ball, 
    otherwise c + r * (q-c)/||q-c||_2
    """
    if c is None:
        normq = linalg.norm(q)
        if normq > r:
            return r * q / normq
        else:
            return q
    else:
        qc = q - c
        normqc = linalg.norm(qc)
        if normqc > r:
            return c + r * qc / normqc
        else:
            return q



def squ_l2_from_subspace(q, l, U):
    """
    prox of q w.r.t a distance from a linear subspace whose orthonormal basis is U:

        arg min_x 0.5*||l.*(I + U*U')*x||_2^2 + 0.5*||x-q||_2^2 = (q + l.*U*(U'*q)) ./ (l+1)

    U : m x r matrix, LinearOperator, or tuple(fU, fUT) of lambda functions fU(x)=U.dot(x) and fUT(y)=U.conj().T.dot(y),
         as an orthonormal basis of an r-dimensional linear subspace of an m-dimensional space.

    For a linear affine subspace with an offset c, use squ_l2_from_subspace(q-c, l, U).
    """

    # define the functions that compute projections by U and its adjoint
    if type(U) is tuple:
        fU = U[0]
        fUT = U[1]
    else:
        Us = splinalg.aslinearoperator(U)
        fU = Us.matvec
        fUT = Us.rmatvec

    return (q + l * fU(fUT(q))) / (l+1.)



def squ_l2(q, l, U=None):
    """
    arg min_x 0.5*||l.*x||_2^2 + 0.5*||x-q||_2^2 = q ./ (l+1)
    """
    if U is None:
        return q / (l+1.)
    else:
        return squ_l2_from_subspace(q, l, U)



def l1(q, l):
    """
    arg min_x ||l.*x||_1 + 0.5*||x-q||_2^2
    """
    return th.soft(q, l)



def l0(q, l):
    """
    arg min_x |||l.*x||_0 + 0.5*||x-q||_2^2 = q .* (q>sqrt(2*l))
    """
    return th.hard(q, np.sqrt(2.*l))



def nuclear(Q, l):
    """
    arg min_x l*||X||_* + 0.5*||X-Q||_F^2
    """
    return th.soft_svd(Q, l)


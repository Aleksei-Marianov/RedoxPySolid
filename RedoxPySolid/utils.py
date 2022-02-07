# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov
# --------------------------------------------------------------------------  

"""
The module provides common utility funcitons for the module:

Functions:
---------
_getFullResponse(timeScale: c_double,
                        resistance: c_double,
                        size: int,
                        unmodifiedSequencePtr: pointer,
                        DLCCorrectedSequencePtr: pointer,
                        e0_array: np.ndarray,
                        k0_array: np.ndarray,
                        g0_array: np.ndarray,
                        a0_array: np.ndarray,
                        z0_array: np.ndarray) -> pointer; Computes a redox 
response of the system upon applicaiton of the external pulse sequence.

_getNumpyArrayFromPtr(input_poiner: pointer) -> np.ndarray; Returns 
a numpy array from the ctypes pointer class object.
"""

from ctypes import c_double, pointer, POINTER, cdll, c_int
import numpy as np
import os

def _getFullResponse(timeScale: c_double,
                        resistance: c_double,
                        size: int,
                        unmodifiedSequencePtr: pointer,
                        DLCCorrectedSequencePtr: pointer,
                        e0_array: np.ndarray,
                        k0_array: np.ndarray,
                        g0_array: np.ndarray,
                        a0_array: np.ndarray,
                        z0_array: np.ndarray) -> pointer:
    numberOfRedoxCouples = len(g0_array)
    e0 = pointer(np.ctypeslib.as_ctypes(e0_array))
    g0 =  pointer(np.ctypeslib.as_ctypes(g0_array))
    a0 =  pointer(np.ctypeslib.as_ctypes(a0_array))
    k0 =  pointer(np.ctypeslib.as_ctypes(k0_array))
    z0 =  pointer(np.ctypeslib.as_ctypes(z0_array))

    redoxComputeLib = os.path.dirname(__file__) + "\clibredoxKinetics.dll"
    ComputationalModule = cdll.LoadLibrary(redoxComputeLib)
    cLibRedoxCompute = ComputationalModule.redoxKineticsFull

    cLibRedoxCompute.argtypes = [c_double, 
                        c_double, 
                        c_int,
                        c_int,
                        POINTER(c_double*size), 
                        POINTER(c_double*size),
                        POINTER(c_double*int(numberOfRedoxCouples)),
                        POINTER(c_double*int(numberOfRedoxCouples)),
                        POINTER(c_double*int(numberOfRedoxCouples)),
                        POINTER(c_double*int(numberOfRedoxCouples)),
                        POINTER(c_double*int(numberOfRedoxCouples))]
    cLibRedoxCompute.restype = POINTER(c_double*size)
    
    responsePtr = cLibRedoxCompute(timeScale,
                            resistance, 
                            numberOfRedoxCouples, 
                            c_int(size), 
                            unmodifiedSequencePtr, 
                            DLCCorrectedSequencePtr, 
                            g0, k0, e0, a0, z0)
    return responsePtr


# read the contents of the pointer
def _getNumpyArrayFromPtr(input_poiner: pointer) -> np.ndarray:
    return np.ctypeslib.as_array(input_poiner.contents)

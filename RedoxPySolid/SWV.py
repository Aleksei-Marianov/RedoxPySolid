# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov
# --------------------------------------------------------------------------  

"""
Compute a standard square wave voltammogram for the electrode with or without a
redox active layer on the surface. The parameters of the surface layer are 
passed as an instance of the class "ElectrochemicallyActiveLayer".
If the surface_layer is None, then only non-faradic current will be 
returned. The latter feature could be used to determine the resistance and 
capacitance of the system while not wasting the time on unnecessary computations.

The SWV class also forms a base class for the SWV-based 2D methods.
"""

from os import path
import numpy as np
from ctypes import cdll, c_double, c_int, pointer, POINTER
from RedoxPySolid.activeLayer import ElectrochemicallyActiveLayer
from RedoxPySolid.utils import _getFullResponse, _getNumpyArrayFromPtr

# define the funcitons creating the input pulse sequence arrays

def _getExperimentClock(pulse_time: c_double,
                        size: int,
                        resolution: c_int,
                        clock: pointer) -> pointer:
    """
    Builds the experimental clock specific for a SWV voltammogram.

    Parameters:
    -----------
    pulse_time: c_double, time period passed between 2 neighbouring sampling points 
                (defined by the scan rate and the scan resolution), seconds;
    size: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    resolution: c_int, the number of points across each potential step;
    clock: pointer, a pointer to the C++ funciton located in 
                    the respective DLL (for Windows) or .so file (MacOS and Linux)
    Returns:
    --------
    pointer to the array of c_doubles with the experimental time sequence.
    """
    clock.argtypes = [c_double,
                        c_int,
                        c_int]
    clock.restype = POINTER(c_double*size)
    experimentClockPtr = clock(pulse_time, c_int(size), resolution)
    return experimentClockPtr

def _getUnmodifiedSWVPulseSequencePtr(e_step: c_double,
                                    amplitude: c_double,
                                    e_start: c_double,
                                    size: int,
                                    resolution: c_int,
                                    inputSequenceFunct: pointer) -> pointer:
    
    """
    Builds the unmodified SWV pulse sequence.

    Parameters:
    -----------
    e_step: c_double, defines how much SWV progresses across one frequency cycle, volt;
    amplitude: c_double, amplitude of SWV, volt;
    e_start: c_double, starting point of SWV, volt (reference electrode is not important);
    size: int, length of the resulting array 
            (required for the static memory allocaiton within the respective C++ funciton);
    resolution: c_int, the number of points across each potential step;
    inputSequenceFunct: pointer, a pointer to the C++ funciton located in 
                        the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the unmodified SWV pulse sequence.
    """
    inputSequenceFunct.argtypes = [c_double, 
                                    c_double, 
                                    c_double, 
                                    c_int, 
                                    c_int]
    inputSequenceFunct.restype = POINTER(c_double*size)
    unmodifiedSequencePtr = inputSequenceFunct(e_step, amplitude, e_start, c_int(size), resolution)
    return unmodifiedSequencePtr

def _getDLCCorrectedPulseSequencePtr(pulse_time: c_double,
                                resistance: c_double,
                                capacitance: c_double,
                                rawSWV: pointer,
                                size: int,
                                resolution: c_int,
                                cLibInputFunct: pointer) -> pointer:
    """
    Builds the SWV pulse sequence with a capacitive correction.

    Parameters:
    -----------
    pulse_time: c_double, time period passed between 2 neighbouring sampling points 
                (defined by the scan rate and the scan resolution), seconds;
    resistance: c_double, resistance of the electrochemical system, Ohm;
    capacitance: c_double, capacitance of the electrochemical system, farad;
    rawSWV: pointer, a C-style pointer to the unmodified SWV pulse sequence;
    size: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    resolution: c_int, the number of points across each potential step;
    cLibInputFunct: pointer, a pointer to the C++ funciton located in the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the DLC-corrected SWV pulse sequence.
    """            
    cLibInputFunct.argtypes = [c_double, 
                                c_double, 
                                c_double, 
                                POINTER(c_double*size), 
                                c_int,
                                c_int]
    cLibInputFunct.restype = POINTER(c_double*size)
    dlcCorrectedSeqPtr = cLibInputFunct(pulse_time, 
                                        resistance, 
                                        capacitance, 
                                        rawSWV, 
                                        c_int(size), 
                                        resolution)
    return dlcCorrectedSeqPtr

# return a pointer to the DLC currents
def _getDLCcurrentPtr(resistance: c_double,
                    size: int,
                    rawSWV: pointer,
                    dlcCorrectedSWV:pointer,
                    cLibInputFunct: pointer) -> pointer:

    """
    Builds a full capacitive current for the system in quesiton.

    Parameters:
    -----------
    pulse_time: c_double, time period passed between 2 neighbouring sampling points 
                (defined by the scan rate and the scan resolution), seconds;
    resistance: c_double, resistance of the electrochemical system, Ohm;
    capacitance: c_double, capacitance of the electrochemical system, farad;
    rawSWV: pointer, a C-style pointer to the unmodified SWV pulse sequence;
    size: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    resolution: c_int, the number of points across each potential step;
    cLibInputFunct: pointer, a pointer to the C++ funciton located in 
                the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the DLC-corrected SWV pulse sequence.
    """
    
    cLibInputFunct.argtypes = [c_double, 
                                c_int,
                                POINTER(c_double*size), 
                                POINTER(c_double*size)]
    cLibInputFunct.restype = POINTER(c_double*size)
    dlcCurrentPtr = cLibInputFunct(resistance,
                                    c_int(size),
                                    rawSWV,
                                    dlcCorrectedSWV)
    return dlcCurrentPtr

def _getSWVdata(swv_full_response: np.ndarray) -> np.ndarray:
    """
    Computes the truncated SWV curve.

    Parameters:
    -----------
    swv_full_response: np.ndarray, full SWV current response;
    
    Returns:
    --------
    np.ndarray, truncated SWV current.
    """

    j_truncated = [np.average(l) for i, l in enumerate(np.reshape(swv_full_response, (-1, 10)), 1) if i % 10 == 0]
    forward = np.array([x for i, x in enumerate(j_truncated) if i % 2 == 0])
    backward = np.array([x for i, x in enumerate(j_truncated) if i % 2 != 0])
    return forward - backward

# return the SWV step funciton for plotting
def _getSWVSteps(e_start: float,
                e_end: float,
                e_step: float) -> np.ndarray:
    """
    Provides the x coordinate for the plotting of the SWV curve.

    Parameters:
    -----------
    e_start: float, defines the starting point for SWV, volt;
    e_end: float, defines the end point of SWV, volt;
    e_step: float, defines how much SWV progresses across one frequency cycle, volt;
    
    Returns:
    --------
    np.ndarray, SWV step punciton without the overlaid square wave component;
    """
    step_count = int(1 + (e_end - e_start)/e_step)
    return np.linspace(e_start, e_end, step_count)


class SWV:
    """
    Class describes the behaviour of the electrode upon applicaiton of 
    the square wave voltammetry pulse sequence. 
    Note: all units are strictly metric (V, F, Ohm, s)!

    Class attributes
    ----------
    None

    Class instance attributes
    ----------
    1) np.ndarrays containing non-faradic responses:
    self.swv_experiment_clock: experiment clock;
    self.swv_pulse_sequence: unmodified SWV pulse sequence;
    self.swv_dlc_corrected_pulse_sequence: full pulse sequence with the capacitive correciton;
    self.swv_capacitive_current: full capacitive current only;
    self.swv_pontential_scale: SWV E scle for plotting;
    self.swv_data: truncated SWV data for non-faradic system (computed if surface_layer == None)
    
    2) np.ndarrays containing faradic responses added on top (if the surface_layer parameter is not None):
    self.swv_full_response: complete swv response with the faradic currents;
    self.swv_data: truncated SWV data with faradic currents;

    Methods
    -------
    __init__(self) -> None. Constructor method bulding the SWV instance attributes.
    """
    def __init__(self, surface_layer: ElectrochemicallyActiveLayer,
                 swv_input_params: dict,
                 resolution  = 100) -> None:
        """
        Build the the SWV scan outputs

        Parameters:
        -----------
        surface_layer: ElectrochemicallyActiveLayer.
            Important: value None could be passed and then only non-faradic responses will be returned;

        swv_input_params: dict, full description of the SWV scan.
            Example:
            swv_params = {'e_start': 0.5,
                    'e_step': -0.01,
                    'e_end': -0.5,
                    'amplitude': 0.025,
                    'log_freq': 2,
                    'resistance': 10,
                    'capacitance': 100*10**(-6)};
        resolution, number of points per each puse, default value 100;
        
        Returns:
        --------
        None, but creates the instance attributes (vide supra);
        """

        # get the method params
        e_start = swv_input_params['e_start']
        e_end = swv_input_params['e_end']
        e_step = swv_input_params['e_step']

        if e_end < e_start:
            assert e_step < 0, "e_step parameter must be negative."
        else:
            assert e_step > 0, "e_step parameter must be positive."
            
        amplitude = swv_input_params['amplitude']
        resistance = swv_input_params['resistance']
        capacitance = swv_input_params['capacitance']
        sizeInputSequence = int(2*resolution*(e_end - e_start + e_step) / e_step)
        pulse_time = 1/(2*10**swv_input_params['log_freq'])
        characteristic_method_time = pulse_time/resolution        

        # initialize the C++ dynamic library
        # a) load swv model DLL
        pulseSeqLib = path.dirname(__file__) + "\clibswv.dll"
        cLibInputFunct = cdll.LoadLibrary(pulseSeqLib)

        # b) extract the input funciton pointers
        clockFunctPtr = cLibInputFunct.experimentClock
        unmodInputSeqFunctPtr = cLibInputFunct.swvInputArray
        dlcCorFunctPtr = cLibInputFunct.swvDLCCorrectedInputArray
        dlcCurrentFunctPtr = cLibInputFunct.swvDLCcurrent
        
        # c) prepare the pointers to the ctypes arrays
        experimentClockPtr = _getExperimentClock(c_double(pulse_time),
                                                sizeInputSequence,
                                                c_int(resolution),
                                                clockFunctPtr)
        
        unmodifiedPulseSequencePtr = _getUnmodifiedSWVPulseSequencePtr(c_double(e_step),
                                                                        c_double(amplitude),
                                                                        c_double(e_start),
                                                                        sizeInputSequence,
                                                                        c_int(resolution),
                                                                        unmodInputSeqFunctPtr)

        dlcCorrectedPulseSequencePtr = _getDLCCorrectedPulseSequencePtr(c_double(pulse_time),
                                                                        c_double(resistance),
                                                                        c_double(capacitance),
                                                                        unmodifiedPulseSequencePtr,
                                                                        sizeInputSequence,
                                                                        c_int(resolution),
                                                                        dlcCorFunctPtr)        
        
        dlcCurSWVPtr = _getDLCcurrentPtr(c_double(resistance),
                                        sizeInputSequence,
                                        unmodifiedPulseSequencePtr,
                                        dlcCorrectedPulseSequencePtr,
                                        dlcCurrentFunctPtr)
        
        self.swv_capacitive_current = _getNumpyArrayFromPtr(dlcCurSWVPtr)
        
        # buld the faradic currents if the ElectrochemicallyActiveLayer is passed
        if not isinstance(surface_layer, type(None)):
            input_data_dict = surface_layer.compressed_data
            e0_array = input_data_dict['E0']
            k0_array = input_data_dict['k0']
            g0_array = input_data_dict['g']
            a0_array = input_data_dict['a']
            z0_array = input_data_dict['z']
            fullResponsePtr = _getFullResponse(c_double(characteristic_method_time),
                                                c_double(resistance),
                                                sizeInputSequence,
                                                unmodifiedPulseSequencePtr,
                                                dlcCorrectedPulseSequencePtr,
                                                e0_array,
                                                k0_array,
                                                g0_array,
                                                a0_array,
                                                z0_array)

            self.swv_full_response = _getNumpyArrayFromPtr(fullResponsePtr)
            self.swv_data = _getSWVdata(self.swv_full_response)
        else:
            self.swv_data = _getSWVdata(self.swv_capacitive_current)

        # compile the public class attributes specific for an SWV without a faradic component
        self.swv_experiment_clock = _getNumpyArrayFromPtr(experimentClockPtr)
        self.swv_pulse_sequence = _getNumpyArrayFromPtr(unmodifiedPulseSequencePtr)
        self.swv_dlc_corrected_pulse_sequence = _getNumpyArrayFromPtr(dlcCorrectedPulseSequencePtr)
        self.swv_pontential_scale = _getSWVSteps(e_start, e_end, e_step)


# testing and example:
if __name__ == "__main__":

    import matplotlib.pyplot as plt

    electrode_params = [{'dist_type': 'normal',
                        'g0': 0.5*10**(-9),
                         'e0': 0.15,
                         'sigma_e0': 0.02,
                         'log_k0': 1,
                         'sigma_log_k0': 0.1,
                         'a': 0.1,
                         'z': 2},
                         {'dist_type': 'normal',
                        'g0': 0.5*10**(-9),
                         'e0': -0.15,
                         'sigma_e0': 0.02,
                         'log_k0': 1,
                         'sigma_log_k0': 0.05,
                         'a': 0.5,
                         'z': 1}]

    swv_params = {'e_start': 0.5,
                'e_step': -0.01,
                'e_end': -0.5,
                'amplitude': 0.025,
                'log_freq': 2,
                'resistance': 10,
                'capacitance': 100*10**(-6)}

    layer = ElectrochemicallyActiveLayer(61, (-0.5, 0.5), 61, (0, 2), electrode_params, loading_cutoff=10**(-15))
    layer.visualise_surface_kinetics()
    
    scan = SWV(layer, swv_params)
    x = scan.swv_pontential_scale
    y = scan.swv_data
    plt.plot(x, y)
    plt.xlabel('E, V')
    plt.ylabel('j, A/cm$^{-2}$')
    plt.tight_layout()
    plt.show()


    y = scan.swv_capacitive_current
    x = scan.swv_experiment_clock
    plt.plot(x, y)
    plt.xlabel('E, V')
    plt.ylabel('j, A/cm$^{-2}$')
    plt.tight_layout()
    plt.show()


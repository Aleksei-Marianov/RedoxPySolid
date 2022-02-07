# --------------------------------------------------------------------------
                    # Written by Aleksei Marianov
# --------------------------------------------------------------------------  

"""
Compute a standard cyclic voltammogram for the electrode with or without a
redox active layer on the surface. The parameters of the surface layer are 
passed as an instance of the class "ElectrochemicallyActiveLayer".
"""

import os
from ctypes import c_double, c_int, pointer, POINTER, cdll
from RedoxPySolid.activeLayer import ElectrochemicallyActiveLayer
from RedoxPySolid.utils import _getFullResponse, _getNumpyArrayFromPtr

def _getExperimentClock(time_increment: c_double,
                        arraySize: int,
                        cClockFunct: pointer) -> pointer:
    """
    Builds the experimental clock specific for a cyclic voltammogram.

    Parameters:
    -----------
    time_increment: c_double, time period passed between 2 neighbouring sampling points 
                (defined by the scan rate and the scan resolution), seconds;
    arraySize: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    cClockFunct: pointer, a pointer to the C++ funciton located in 
                    the respective DLL (for Windows) or .so file (MacOS and Linux)
    Returns:
    --------
    pointer to the array of c_doubles with the experimental time sequence.
    """

    cClockFunct.argtypes = [c_double,
                            c_int]
    cClockFunct.restype = POINTER(c_double*arraySize)
    clockPtr = cClockFunct(time_increment, c_int(arraySize))
    return clockPtr

def _getRawCV(e_start: c_double,
            e_end: c_double,
            digital_resolution: c_int,
            arraySize: int,
            cvInputFunctPtr: pointer) -> pointer:
    
    """
    Builds the unmodified CV pulse sequence.

    Parameters:
    -----------
    e_start: c_double, scan starting potential, V;
    e_end: c_double, scan reverse point, V;
    digital_resolution: c_int, scan resolution, points/V;
    arraySize: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    cvInputFunctPtr: pointer , a pointer to the C++ funciton located in 
                the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the unmodified CV sequence.
    """

    cvInputFunctPtr.argtypes = [c_double,
                                c_double,
                                c_int,
                                c_int]
    cvInputFunctPtr.restype = POINTER(c_double*arraySize)
    cvRawPtr = cvInputFunctPtr(e_start, e_end, digital_resolution, c_int(arraySize))
    return cvRawPtr

def _getDLCcorrectedCV(resistance: c_double,
                        capacitance: c_double,
                        time_increment: c_double,
                        arraySize: int,
                        rawCVsequence: pointer,
                        cvDLCcorrectionFunctPtr: pointer) -> pointer:
    
    """
    Adds a capacitive correction to the CV sequence.

    Parameters:
    -----------
    resistance: c_double, resistance of th system, Ohm;
    capacitance: c_double, capacitance of the systm, Farad;
    time_increment: c_double, time period passed between 2 neighbouring sampling points 
                (defined by the scan rate and the scan resolution), seconds;
    arraySize: int,length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    rawCVsequence: pointer, address of the array containing the unmodified CV sequence;
    cvDLCcorrectionFunctPtr: pointer, pointer to the C++ funciton introducing the capacitive correction;
    cLibInputFunct: pointer, a pointer to the C++ funciton 
        located in the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the DLC-corrected CV sequence.
    """

    cvDLCcorrectionFunctPtr.argtypes = [c_double,
                                        c_double,
                                        c_double,
                                        c_int,
                                        POINTER(c_double*arraySize)]
    cvDLCcorrectionFunctPtr.restype = POINTER(c_double*arraySize)
    dlcCorCVPtr = cvDLCcorrectionFunctPtr(resistance, capacitance, time_increment, c_int(arraySize), rawCVsequence)
    return dlcCorCVPtr

def _getDLCcurrent(resistance: c_double,
                    arraySize: int,
                    rawCVPtr: pointer,
                    dlcCorCVPtr: pointer,
                    cvDLCCurrentFunctPtr: pointer) -> pointer:

    """
    Builds a capacitive component of the CV response.

    Parameters:
    -----------
    resistance: c_double, resistance of th system, Ohm;
    arraySize: int, length of the resulting array 
                (required for the static memory allocaiton within the respective C++ funciton);
    rawCVPtr: pointer, address of the array containing unmodified CV pulse sequnce;
    dlcCorCVPtr: pointer, address of the array containing DLC corrected Cv curve;
    cvDLCCurrentFunctPtr: pointer, a pointer to the C++ funciton comuting DLC current and
        located in the respective DLL (for Windows) or .so file (MacOS and Linux)
    
    Returns:
    --------
    pointer to the array of c_doubles with the DLC current for the CV.
    """

    cvDLCCurrentFunctPtr.argtypes = [c_double,
                                    c_int,
                                    POINTER(c_double*arraySize),
                                    POINTER(c_double*arraySize)]
    cvDLCCurrentFunctPtr.restype = POINTER(c_double*arraySize)
    cvDLCCurrentPtr = cvDLCCurrentFunctPtr(resistance, c_int(arraySize), rawCVPtr, dlcCorCVPtr)
    return cvDLCCurrentPtr

class CV:

    """
    Class describes the behaviour of the electrode upon applicaiton of 
    the square wave voltammetry pulse sequence. 
    Note: all units are strictly metric (V, F, Ohm, s)!

    Class attributes
    ----------
    None

    Class instance attributes
    ----------
    self.cv_experiment_clock: np.ndarray, timescale of the CV;
    self.cv_pulse_sequence: np.ndarray, unmodified CV sequence,
        forms the x coordinate for the CV plotting;
    self.cv_dlc_corrected_pulse_sequence: np.ndarray, CV potential sequence with the added capacitive correction;
    self.cv_capacitive_current: np.ndarray, purely non-faradic CV component;
    self.cv_full_response: np.ndarray, full CV response.

    Methods
    -------
    __init__(self) -> None. Constructor method bulding the CV instance attributes.
    """

    def __init__(self,
                surface_layer: ElectrochemicallyActiveLayer,
                cv_input_params: dict,
                resolution = 50000) -> None:

        """
        Build the the CV output.

        Parameters:
        -----------
        surface_layer: ElectrochemicallyActiveLayer.
            Important: value None could be passed and then only non-faradic responses will be returned;

        cv_input_params: dict, full description of the CV scan.
            Example:
            cv_params = {'e_start': 0.5,
                        'e_end': -0.3,
                        'scan_rate': 0.1,
                        'resistance': 10,
                        'capacitance': 100*10**(-6)};
        resolution, number of point per V of scan, default 50000;
        
        Returns:
        --------
        None, but creates the instance attributes (vide supra);
        """

        e_start = cv_input_params['e_start']
        e_end = cv_input_params['e_end']
        scan_rate = cv_input_params['scan_rate']
        resistance = cv_input_params['resistance']
        capacitance = cv_input_params['capacitance']
        time_increment= 1/(scan_rate*resolution)
        arryaSize = int(2*abs(e_start - e_end)*resolution + 1)
        

        input_data_dict = surface_layer.compressed_data
        e0_array = input_data_dict['E0']
        k0_array = input_data_dict['k0']
        g0_array = input_data_dict['g']
        a0_array = input_data_dict['a']
        z0_array = input_data_dict['z']

        # initialize the C++ dynamic libraries
        # a) load DLLs
        pulseSeqLib = os.path.dirname(__file__) + "\clibcv.dll"
        cLibInputFunct = cdll.LoadLibrary(pulseSeqLib)

        # b) extract the input funciton pointers
        clockFunctPtr = cLibInputFunct.experimentClock
        unmodInputSeqFunctPtr = cLibInputFunct.rawCVsequence
        dlcCorFunctPtr = cLibInputFunct.dlcCorrectedCVsequence
        dlcCurrentFunctPtr = cLibInputFunct.dlcCurrentCV

        # get input arrays
        clockPtr = _getExperimentClock(c_double(time_increment), arryaSize, clockFunctPtr)
        raw_cv_ptr = _getRawCV(c_double(e_start), 
                                c_double(e_end), 
                                c_int(resolution), 
                                arryaSize, 
                                unmodInputSeqFunctPtr)
        dlc_corrected_cv_ptr = _getDLCcorrectedCV(c_double(resistance), 
                                                    c_double(capacitance),
                                                    c_double(time_increment),
                                                    arryaSize,
                                                    raw_cv_ptr,
                                                    dlcCorFunctPtr)
        dlc_current_ptr = _getDLCcurrent(c_double(resistance),
                                            arryaSize,
                                            raw_cv_ptr,
                                            dlc_corrected_cv_ptr,
                                            dlcCurrentFunctPtr)
        
        total_currentPtr = _getFullResponse(c_double(time_increment), 
                                            c_double(resistance),
                                            arryaSize,
                                            raw_cv_ptr, dlc_corrected_cv_ptr, 
                                            e0_array, k0_array, g0_array,
                                            a0_array, z0_array)

        # define public class attributes
        self.cv_experiment_clock = _getNumpyArrayFromPtr(clockPtr)
        self.cv_pulse_sequence = _getNumpyArrayFromPtr(raw_cv_ptr)
        self.cv_dlc_corrected_pulse_sequence = _getNumpyArrayFromPtr(dlc_corrected_cv_ptr)
        self.cv_capacitive_current = _getNumpyArrayFromPtr(dlc_current_ptr)
        self.cv_full_response = _getNumpyArrayFromPtr(total_currentPtr)
       
        
# debugging and testing
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    electrode_params = [
        {'dist_type': 'normal',
                        'g0': 3*10**(-9),
                         'e0': 0.1,
                         'sigma_e0': 0.01,
                         'log_k0': 1,
                         'sigma_log_k0': 0.05,
                         'a': 0.5,
                         'z': 1}]
    
    electrode_params_2 = [
        {'dist_type': 'normal',
                        'g0': 1.5*10**(-9),
                         'e0': 0.1,
                         'sigma_e0': 0.01,
                         'log_k0': 1,
                         'sigma_log_k0': 0.05,
                         'a': 0.5,
                         'z': 2}]
    
    electrode_params_3 = [
        {'dist_type': 'normal',
                        'g0': 1*10**(-9),
                         'e0': 0.1,
                         'sigma_e0': 0.01,
                         'log_k0': 1,
                         'sigma_log_k0': 0.05,
                         'a': 0.5,
                         'z': 3}]
    
    cv_params = {'e_start': 0.5,
                'e_end': -0.3,
                'scan_rate': 0.1,
                'resistance': 10,
                'capacitance': 100*10**(-6)}

    electrode = ElectrochemicallyActiveLayer(51, (0.5, -0.5), 51, (0, 2), electrode_params, None)
    electrode2 = ElectrochemicallyActiveLayer(51, (0.5, -0.5), 51, (0, 2), electrode_params_2, None)
    electrode3 = ElectrochemicallyActiveLayer(51, (0.5, -0.5), 51, (0, 2), electrode_params_3, None)

    cv = CV(electrode, cv_params)
    cv1 = CV(electrode2, cv_params)
    cv3 = CV(electrode3, cv_params)

    x = cv.cv_pulse_sequence
    
    y1 = cv.cv_full_response*1000
    y2 = cv1.cv_full_response*1000
    y3 = cv3.cv_full_response*1000

    # y = cv.raw_cv[1]
    # y1 = cv.dlc_corrected_cv[1]
    
    # print(y2)
    # # plt.plot(x, y)
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.plot(x, y3)
    plt.show()
#ifndef SHARED_LIB_H
#define SHARED_LIB_H

# include <cmath>
# include "definitions.h"

using namespace std;

#ifdef __cplusplus

extern "C" {

#ifdef BUILD_MY_DLL
    #define SHARED_LIB __declspec(dllexport)
#else 
    #define SHARED_LIB __declspec(dllimport)
#endif

double* SHARED_LIB experimentClock(double pulseTime,
									int arrLength,
									int npp);

double* SHARED_LIB swvInputArray(double e_step, 
								double amplit, 
								double e_start, 
								int arraySize,
								int npp);

double* SHARED_LIB swvDLCCorrectedInputArray(double pulse_time,
												double resistance,
												double capacitance,
												double* inputSignal,
												int arraySize,
												int npp);

double* SHARED_LIB swvDLCcurrent(double resistance,
									int arraySize,
									double* inputSignal,
									double* dlcCorrectedSignal);

}



#endif

#endif
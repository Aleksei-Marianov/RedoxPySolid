#ifndef SHARED_LIB_CV_H
#define SHARED_LIB_CV_H

#include <cmath>
#include "definitions.h"

using namespace std;

#ifdef __cplusplus

extern "C" {

#ifdef BUILD_MY_DLL
    #define SHARED_LIB_CV __declspec(dllexport)
#else 
    #define SHARED_LIB_CV __declspec(dllimport)
#endif

double* SHARED_LIB_CV experimentClock(double timeIncrement,
                                    int arraySize);

double* SHARED_LIB_CV rawCVsequence(double e_start,
                                    double e_end,
                                    int digitalResolution,
                                    int arraySize);

double* SHARED_LIB_CV dlcCorrectedCVsequence(double resistance,
                                            double capacitance,
                                            double timeIncrement,
                                            int arraySize,
                                            double* inputCVsequence);

double* SHARED_LIB_CV dlcCurrentCV(double resistance,
                                int arraySize,
                                double* rawCV,
                                double* DLCcorrectedCV);

}

#endif

#endif
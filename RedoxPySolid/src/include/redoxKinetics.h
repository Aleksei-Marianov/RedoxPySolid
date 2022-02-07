#ifndef SHARED_REDOX_H
#define SHARED_REDOX_H

# include <cmath>
#include "definitions.h"

using namespace std;

#ifdef __cplusplus

extern "C" {

#ifdef BUILD_MY_DLL
    #define SHARED_REDOX __declspec(dllexport)
#else 
    #define SHARED_REDOX __declspec(dllimport)
#endif

double* SHARED_REDOX redoxKineticsFull(double timePeriod,
                double resistance,
                int sizeOfInputArray,
                int lenOfPulseSequence,
                double* inputPulseSequence,
                double* DLCcorrectedSequence,
                double* loadingsArray,
                double* kineticConstArray,
                double* redoxPotArray,
                double* symCoefArray,
                double* zArray);

double startingRedConcentration (double overpotential,
                                double componentLoading, 
                                int z);

double instantaneousRedConc(double red0,
                            double g,
                            double Kratio,
                            double Ksum,
                            double time);
}



#endif

#endif
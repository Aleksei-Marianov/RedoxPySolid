#include "include\cv.h"

// build reference timescale
double* experimentClock(double timeIncrement,
                        int arraySize)
{   
    double* clock = new double[arraySize];
    for (int i = 0; i < arraySize; i++)
        {
            clock[i] = i*timeIncrement;
        }
    return clock;
}

// start scan at e_start, sweep to e_end. Resolution is given as points/V
double* rawCVsequence(double e_start,
                    double e_end,
                    int digitalResolution,
                    int arraySize)
{
    // create a container for the unmodified CV sequence and placeholders for the arary length
    double* rawCVsequence = new double[arraySize];
    int forwardLen = 0;
    int backwardLen = 0;
    double eIncrement = 1.0f/(double)digitalResolution;

    if (e_start < e_end)
    {   
        int forwardLen = round((e_end - e_start)*digitalResolution + 1);
        int backwardLen = forwardLen - 1;
        
        for (int i = 0; i < forwardLen; i++) 
        {
            rawCVsequence[i] = e_start + i*eIncrement;
        }
        for (int i = 1; i <= backwardLen; i++)
        {
            rawCVsequence[forwardLen + i - 1] = e_end - i*eIncrement;
        }

    } else 
    {
        int forwardLen = (e_start - e_end)*digitalResolution + 1;
        int backwardLen = forwardLen - 1;

        for (int i = 0; i < forwardLen; i++) 
        {
            rawCVsequence[i] = e_start - i*eIncrement;
        }
        for (int i = 1; i <= backwardLen; i++)
        {
            rawCVsequence[forwardLen + i - 1] = e_end + i*eIncrement;
        }
    }

    return rawCVsequence;
}

double* dlcCorrectedCVsequence(double resistance,
                            double capacitance,
                            double timeIncrement,
                            int arraySize,
                            double* inputCVsequence)
{   
    double decayTerm = 1 - exp(-(timeIncrement / (resistance * capacitance)));
    double* dlcCorrectedCV = new double [arraySize];
    dlcCorrectedCV[0] = inputCVsequence[0];

    for (int i = 1; i < arraySize; i++)
    {
        dlcCorrectedCV[i] = dlcCorrectedCV[i-1] + (inputCVsequence[i] - dlcCorrectedCV[i-1])*decayTerm;
    }
    return dlcCorrectedCV;
}

double* dlcCurrentCV(double resistance,
                    int arraySize,
                    double* rawCV,
                    double* DLCcorrectedCV)
{   
    double* DLCcurrent = new double[arraySize];

    for (int i = 0; i < arraySize; ++i)
    {
        DLCcurrent[i] = (rawCV[i] - DLCcorrectedCV[i])/resistance;
    }
    return DLCcurrent;
}
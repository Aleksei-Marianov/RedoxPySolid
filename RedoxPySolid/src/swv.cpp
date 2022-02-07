# include "include/swv.h"

// generate experiment clock, pulse time is given in seconds
double* experimentClock(double pulseTime,
						int arrLength,
						int npp)
{
	double* clockContainer = new double[arrLength];
	double intervalDuration = pulseTime/npp;
	double pushValue = 0;
	for (int i = 0; i < arrLength; i++){
		clockContainer[i] = pushValue;
		pushValue += intervalDuration;
	}
	return clockContainer;
}

// generate the complete input VF-SWV array
double* swvInputArray(double e_step, 
						double amplit, 
						double e_start, 
						int arraySize,
						int npp)
{
	// cleate a container for the input sequence
	double* inputSequenceContainer = new double[arraySize];
	// add the square wave component first
	if (e_step < 0)
		{
			int heavisideFlag = 1;
			for (int i = 0; i< arraySize; i++)
				{	
					if (i%npp == 0) heavisideFlag = -heavisideFlag;
					inputSequenceContainer[i] = amplit * heavisideFlag;
				}
		} 
		
		else
		{
			int heavisideFlag = -1;
			for (int i = 0; i< arraySize; i++)
				{	
					if (i%npp == 0) heavisideFlag = -heavisideFlag;
					inputSequenceContainer[i] = amplit * heavisideFlag;
				}
		}

	// add the step function component
	double pushValue = e_start - e_step;
	for (int i = 0; i< arraySize; i++)
		{	
			if (i%(2*npp) == 0) pushValue += e_step;
			inputSequenceContainer[i] += pushValue;
		}

	return inputSequenceContainer;
}

double* swvDLCCorrectedInputArray(double pulse_time,
								double resistance,
								double capacitance,
								double* inputSignal,
								int arraySize,
								int npp)
{
	// placeholders for the potential change during the sweep and the modified sequence
	double deltaE = 0;
	double* correctedSequenceContainer = new double[arraySize];

	double decayTerm = 1- exp(-(pulse_time/npp) / (resistance * capacitance));

	for (int i = 0; i < arraySize; i++)
	{
		if (i == 0) correctedSequenceContainer[0] = inputSignal[0];
			else
			{
				deltaE = inputSignal[i] - correctedSequenceContainer[i-1];
				correctedSequenceContainer[i] = correctedSequenceContainer[i - 1] + deltaE * decayTerm;
			}
	}
	return correctedSequenceContainer;
}

double* swvDLCcurrent(double resistance,
						int arraySize,
						double* inputSignal,
						double* dlcCorrectedSignal)
{
	double* DLCcurrentPlaceholder = new double [arraySize];

	for (int i = 0; i < arraySize; i++)
	{
		DLCcurrentPlaceholder[i] = (inputSignal[i] - dlcCorrectedSignal[i])/resistance;
	}
	return DLCcurrentPlaceholder;
}
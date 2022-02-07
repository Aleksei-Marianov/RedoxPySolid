#include "include/redoxKinetics.h"

// generate a full redox and non-faradic response
// time period is given in seconds
double* redoxKineticsFull(double timePeriod,
                            double resistance,
                            int sizeOfInputArray,
                            int lenOfPulseSequence,
                            double* inputPulseSequence,
                            double* DLCcorrectedSequence,
                            double* loadingsArray,
                            double* kineticConstArray,
                            double* redoxPotArray,
                            double* symCoefArray,
                            double* zArray)
{
    double* overpotentials = new double [lenOfPulseSequence];
    
    // allocate memory for the corrected pulse sequence and initialize it to the initial potential values
    double* averagedPulseSequence = new double [lenOfPulseSequence];
    double* overcorrectedPulseSequence = new double [lenOfPulseSequence];

    for (int i = 0; i < lenOfPulseSequence; i++) 
    {
        averagedPulseSequence[i] = DLCcorrectedSequence[i];
        overcorrectedPulseSequence[i] = DLCcorrectedSequence[i];
    }
    // allocate memory for the arrays with kinetic constants
    double* forwardK= new double [lenOfPulseSequence];
    double* backwardK = new double [lenOfPulseSequence];
    double* Ksum = new double [lenOfPulseSequence];
    double* Kratio = new double [lenOfPulseSequence];

    // allocate memory for the assessmeent of half-lives at each potential 
    double* forwardKhalflife = new double [lenOfPulseSequence];
    double* backwardKhalflife = new double [lenOfPulseSequence];

    // the time benhcmark could be fine-tuned later on
    const double timeBenchmark = 10*timePeriod;
    const bool positiveScanDirection = DLCcorrectedSequence[0] > DLCcorrectedSequence[lenOfPulseSequence];
    
    double* cur = new double [lenOfPulseSequence];
    for (int i = 0; i< lenOfPulseSequence; i++) cur[i] = 0;

    for (int i = 0; i < sizeOfInputArray; i++)
    {     
        // create flags for the lookup bounds and initialise them to 0
        volatile int lookupMinTreshhold = 0;
        volatile int lookupMaxTreshold = lenOfPulseSequence;
        volatile bool LookupThresholdFound = false;

        // compute the half lives for all components and  run a check where
        // it makes sense to compute the reaction rates and where the current is known to be negligeble
        for (int j = 0; j < lenOfPulseSequence; j++)
        {  
            overpotentials[j] = averagedPulseSequence[j] - redoxPotArray[i];
        }

        for (int j = 0; j < lenOfPulseSequence; j++)
        {  
            backwardK[j] = kineticConstArray[i] * exp(-overpotentials[j] * FbyRT*zArray[i] * (1-symCoefArray[i]));
            forwardK[j] = kineticConstArray[i] * exp(overpotentials[j] * FbyRT*zArray[i] * symCoefArray[i]);

            // populate the laf-life arrays
            forwardKhalflife[j] = ln2/forwardK[j];
            backwardKhalflife[j] = ln2/backwardK[j];
        }

        // Optimisation 1
        // assess the value of the kinetic constants before the scan.
        // Scan the array of constants from start to the middle and find the first place where the current 
        // becomes significant enough
        // check the array from the end to the beginning and determine the fist instance where the currents are 
        // no loneger making sense to compute.
        // In both cases break the loop as soon as the first worthwhile instance is discovered.
        // Depending on the scan direciton assess the forward or reverse half-lives first
        
        switch (positiveScanDirection)
            {
            case false:
            // forward scan 
            for (int j = 0; j < lenOfPulseSequence; j++)
                {   
                    if (forwardKhalflife[j] > timeBenchmark*(1-symCoefArray[i])) 
                    {
                        lookupMinTreshhold = j;
                        LookupThresholdFound = true;
                        break;
                    }
                }
            // reverse scan
            for (int j = lenOfPulseSequence; j > 0; j--)
                {
                    if (backwardKhalflife [j] > timeBenchmark*symCoefArray[i])
                    { 
                        lookupMaxTreshold = j;
                        LookupThresholdFound = true;
                        break;
                    }
                }
            break;
            case true:
                // forward scan 
                for (int j = 0; j < lenOfPulseSequence; j++)
                    {   
                        if (backwardKhalflife[j] > timeBenchmark*symCoefArray[i]) 
                        {
                            
                            lookupMinTreshhold = j;
                            LookupThresholdFound = true;
                            break;
                        }
                    }
                // reverse scan
                for (int j = lenOfPulseSequence; j > 0; j--)
                    {
                        if (forwardKhalflife [j] > timeBenchmark*(1-symCoefArray[i]))
                        { 
                            lookupMaxTreshold = j;
                            LookupThresholdFound = true;
                            break;
                        }
                    }
                break;
            }

        // Optimisation  2
        // Compute how many iterations we have to do on a single redox-active couple. 
        // Truncate values close to 0.1 nmol/cm2 for large components. Leave small components as is.
        // Loadings are given as g*10**(-9) mol/cm2.
        // Approach: find ceiling and divide the loading by this value.

        int loadingDivider = ceil(20*loadingsArray[i]*1000000000);        
        if (loadingDivider%2 != 0) ++loadingDivider;
        // The below statement could be modified to add lookup to avoid costly division cycle
        double truncatedComponent = 2*loadingsArray[i]/loadingDivider;

        LOG(loadingDivider);

        // Optimisation 1 implemented: restrict the array lookup to the areas of interest only
        
        for (int j = 0; j < lenOfPulseSequence; j++)
        {
            Ksum[j] = forwardK[j] + backwardK[j];
            Kratio[j] = backwardK[j] /Ksum[j];
        }

        // compute the E corrections for all points on the curve
        // ignore this step if there are no components of interest

        for (int j = 0; j < loadingDivider; j++)
        {
        // get the initial Red surface concentration
        double Red0 = startingRedConcentration(overpotentials[lookupMinTreshhold], 
                                                truncatedComponent, 
                                                zArray[i]);
        

        // if at least one lookup threshold is found -> compute the reaction kinetics
        
        if (LookupThresholdFound)
            {
                if (j%2 == 0)
                    {  
                    
                        for (int n = lookupMinTreshhold+1 ; n <= lookupMaxTreshold; n++)
                            {   
                                
                                // current is computed at the beginning of the timepoint
                                double current = zArray[i] * f * (Red0 * forwardK[n] - (truncatedComponent - Red0) * backwardK[n]);
                                cur[n] = current;
                                
                                // find how much product is actually produced with the finite reaction rate
                                // and push the value on the stack

                                Red0 = instantaneousRedConc(Red0,
                                                            truncatedComponent,
                                                            Kratio[n],
                                                            Ksum[n],
                                                            timePeriod);
                            }
                        for (int m = lookupMinTreshhold; m < lookupMaxTreshold; m++)
                            {
                                // introduce the first resistive correciton
                                overcorrectedPulseSequence[m] = overcorrectedPulseSequence[m] - cur[m] * resistance;
                                
                                // recompute the kinetic constants with the corrected values of the potentials in mind
                                overpotentials[m] = overcorrectedPulseSequence[m] - redoxPotArray[i];
                                forwardK[m] = kineticConstArray[i] * exp(overpotentials[m] * FbyRT*zArray[i] * symCoefArray[i]);
                                backwardK[m] = kineticConstArray[i] * exp(-overpotentials[m] * FbyRT*zArray[i] * (1-symCoefArray[i]));
                                Ksum[m] = forwardK[m] + backwardK[m];
                                Kratio[m] = backwardK[m] /Ksum[m];
                            }
                    }
                    else
                        {
                        for (int n = lookupMinTreshhold+1; n <= lookupMaxTreshold; n++)
                            {   
                                // repeat the same calcualtion for the current and the concentraiton of the component
                                double current = zArray[i] * f * (Red0 * forwardK[n] - (truncatedComponent - Red0) * backwardK[n]);
                                cur[n] = current;
                                
                                Red0 = instantaneousRedConc(Red0,
                                                            truncatedComponent,
                                                            Kratio[n],
                                                            Ksum[n],
                                                            timePeriod);
                            }

                        for (int m = lookupMinTreshhold; m < lookupMaxTreshold; m++)
                            {
                                // introduce the second resistive correciton (get underestimated resistive correction)
                                averagedPulseSequence[m] = overcorrectedPulseSequence[m] - cur[m] * resistance;
                                // averge out the corrected sequences and push the values in both placeholders
                                averagedPulseSequence[m] = (averagedPulseSequence[m] + overcorrectedPulseSequence[m])/2;
                                overcorrectedPulseSequence[m] = averagedPulseSequence[m];

                                // // recompute the kinetic constants again, this time for the undercorrected system
                                overpotentials[m] = averagedPulseSequence[m] - redoxPotArray[i];
                                forwardK[m] = kineticConstArray[i] * exp(overpotentials[m] * FbyRT*zArray[i] * symCoefArray[i]);
                                backwardK[m] = kineticConstArray[i] * exp(-overpotentials[m] * FbyRT*zArray[i] * (1-symCoefArray[i]));
                                Ksum[m] = forwardK[m] + backwardK[m];
                                Kratio[m] = backwardK[m] /Ksum[m];
                            }
                        }
            }  
        }
    }

    // compute all currents based on the Ohm's Law.
    for (int i = 0; i < lenOfPulseSequence; i++)
    {
        averagedPulseSequence[i] = (inputPulseSequence[i] - averagedPulseSequence[i])/resistance;
    }

    // clear the memory allocations
    delete [] overcorrectedPulseSequence;
    delete [] overpotentials;
    delete [] forwardKhalflife;
    delete [] backwardKhalflife;
    delete [] Ksum;
    delete [] Kratio;
    delete [] forwardK;
    delete [] backwardK;
    delete [] cur;

    return averagedPulseSequence;
}

// determine the equilibrium concentraitons of the Red componnet at the start of the window of interest
// concentration is computed in nmol/cm2

  double startingRedConcentration ( double overpotential,
                                    double componentLoading, 
                                    int z)
{
    double redStart = componentLoading/ (1 + exp(z * FbyRT * overpotential));
    return redStart;
}

// compute instanteneous [Red]
 double instantaneousRedConc(double red0,
                            double g,
                            double Kratio,
                            double Ksum,
                            double time)
{   
     double gKratio = g * Kratio;
     double red = gKratio + (red0 - gKratio)*exp(-Ksum*time);
    return red;
}
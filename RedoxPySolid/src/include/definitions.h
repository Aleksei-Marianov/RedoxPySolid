#ifndef TYPEDEF_MACRO_H
#define TYPEDEF_MACRO_H

// change to 0 if the debug is not needed anymore
# define PROJECT_DEBUG 0
#if PROJECT_DEBUG
    #include <iostream>
    #define LOG(message) cout << "Log message: " << message << "\n"
#else
    #define LOG(message)
#endif

// definitions of the electrochemical constants
// if update is needed, the values could be changed and the dlls recompiled
const double r = 8.3145;
const double t = 295.0;
const double rt = r * t;
const double f = 96485.0;
const double FbyRT = f/rt;
const double ln2 = 0.69314718056;

#endif
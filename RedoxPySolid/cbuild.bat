g++ -c -O3  -DBUILD_MY_DLL -I ./src src/swv.cpp
g++ -shared -o clibswv.dll swv.o
g++ -c -O3  -DBUILD_MY_DLL -I ./src src/redoxKinetics.cpp
g++ -shared -o clibredoxKinetics.dll redoxKinetics.o
g++ -c -O3  -DBUILD_MY_DLL -I ./src src/cv.cpp
g++ -shared -o clibcv.dll cv.o
del swv.o
del redoxKinetics.o
del cv.o

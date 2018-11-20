
* test run:
python myolistener.py (get data from myo, send over OSC)
python shape_myo_test.py (run Csound, get myo data over OSC, map to synthesis parameters)

* mapping of parameters set in modmatrix_myotest.txt
where there are 3 lines, one for each sensor input
each line has 10 values, representing the scaling of each sensor to each parameter
Parameter list is currently in submono.inc, where the audio is also generated.

********* original intention for readme:

Shape

Self-learning instrument. 
Take gestural input, learn how to map gestural sensor data (control channels) to synthesis parameters by evoling a modulation matrix.
Audio output is analyzed, and the modmatrix optimization function is to make the audio analysis have the same gestural shapes as the gesture sensor data.
When actual realtime sensor data is fed through the system, we assume that variations from the learned state will provide musical variation of the output.

Usage:

python shape_learn.py
- use saved sensor data (gesture) to synthesize sound and update the modmatrix to optimize the gestural similarity between sensor data and audio data
Shape

Self-learning instrument. 
Take gestural input, learn how to map gestural sensor data (control channels) to synthesis parameters by evoling a modulation matrix.
Audio output is analyzed, and the modmatrix optimization function is to make the audio analysis have the same gestural shapes as the gesture sensor data.
When actual realtime sensor data is fed through the system, we assume that variations from the learned state will provide musical variation of the output.

Usage:

python shape_learn.py
- use saved sensor data (gesture) to synthesize sound and update the modmatrix to optimize the gestural similarity between sensor data and audio data
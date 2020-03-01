
ZMQ scripts for communication between host (sensors and synth) and docker (AI):
- zmqMouse.py: capture mouse data and send over ZMQ *Run on host*
- zmqMyo.py: capture mouse data and send over ZMQ *Run on host*
- zmqKeyboard.py: capture keypress (space, zero) to control record enable/disable, send over ZMQ *Run on host*
- zmqServerSynthparmToOSC.py: receive 25 synth parms on ZMQ, send over OSC to /shapesynth (VST) *Run on host*

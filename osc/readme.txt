
ØMK scripts for communication between host (sensors and synth) and docker (AI):
- zmqMouse.py: capture mouse data and send over ØMK on port 8802 *Run on host*
- zmqServerTestmapping.py: 2 input, 25 output mockup replacement of the AI mapper *Run on docker*
- zmqServerSynthparmToOSC.py: receive 25 synth parms on ØMK, send over OSC to /shapesynth (VST) *Run on host*
- zmqServerSimpletest.py: just for testing/monitoring

OSC scripts for shape:
- oscTest.py: simplest osc test, sending 100 values
- oscMouse.py: capture mouse data and send over OSC on port 8291 *Run on host*
- oscServerTestmapping.py: 2 input, 25 output mockup replacement of the AI mapper *Run on docker*
- oscServerSimpletest.py: just for testing OSC receive, use as monitor utility for debugging port numbers

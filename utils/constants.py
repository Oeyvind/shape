from collections import namedtuple

GESTURE_SAMPLING_FREQUENCY=25 # Hz

psynth = namedtuple('Synth', ['name', 'n_parameters'])

ADDITIVE = psynth('additive', 14)
SUBMONO = psynth('submono', 10)
SINE = psynth('sine', 2)
PARTIKKEL = psynth('partikkel', 25)

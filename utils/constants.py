from collections import namedtuple
from pathlib import Path

GESTURE_SAMPLING_FREQUENCY = 25 # Hz
HISTORY_LENGTH = 30
MASK_VALUE = -100

psynth = namedtuple('Synth', ['name', 'n_parameters'])

ADDITIVE = psynth('additive', 14)
SUBMONO = psynth('submono', 10)
SINE = psynth('sine', 2)
PARTIKKEL = psynth('partikkel', 25)

PROJECT_ROOT = Path(__file__).parent.parent

from collections import namedtuple
from pathlib import Path

GESTURE_SAMPLING_FREQUENCY = 15 # Hz
HISTORY_LENGTH = 10
MASK_VALUE = -100
N_CLASSES = 10
N_EXAMPLES = 15

psynth = namedtuple('Synth', ['name', 'n_parameters'])

ADDITIVE = psynth('additive', 14)
SUBMONO = psynth('submono', 10)
SINE = psynth('sine', 2)
PARTIKKEL = psynth('partikkel', 25)
SYNTH_INSTR = SUBMONO
PITCH_OVERRIDE = 0

PROJECT_ROOT = Path(__file__).parent.parent

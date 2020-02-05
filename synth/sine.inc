; parameter ranges, mapping
gSParmnames[] fillarray "amp","cps"
gkParm_min[] fillarray 0, 50
gkParm_max[] fillarray 1, 1500
gSParm_map[] fillarray "dB", "log"

; read from table, scale and map according to mapping type
kamp read_and_map 0
kcps read_and_map 1

; synthesis
a1 oscili 1, kcps, gisine

amp = interp(kamp)
a1 = a1*amp
a2 = a1

chnset a1, "a1"
chnset a2, "a2"

outch 1, a1*amp, 2, a2*amp

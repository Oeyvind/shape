; parameter ranges, mapping
gSParmnames[] fillarray "amp","cps"
gkParm_min[] fillarray 0, 50
gkParm_max[] fillarray 1, 1200
gSParm_map[] fillarray "lin", "log"

; default values for unmapped parms
tablew 0.5, 0, giParm_values
tablew 0.3, 1, giParm_values

kpitchoverride = p4
if kpitchoverride == 1 then
  kpitch = 0.3
  tablew kpitch, 1, giParm_values
elseif kpitchoverride == 2 then
  kpitch chnget "pitch"
  tablew kpitch, 1, giParm_values
endif

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

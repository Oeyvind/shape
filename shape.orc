
sr = 44100
ksmps = 100
nchnls = 2
0dbfs = 1

giSine ftgen 0, 0, 65536, 10, 1

; auto rewrite from Python
ginum_parms = 10
ginum_sensors = 3
; auto rewrite end

; parameter ranges, mapping
gSParmnames[] fillarray "amp","cps","phasedist","filter1fq","ring","pw1","pw2","filter2fq","filter2res","filter2dist"
gkParm_min[] fillarray 0, 50, 0, 20, 0, 0, 0, 20, 0
gkParm_max[] fillarray 1, 5000, 1, 20000, 1, 1, 1, 20000, 1
gSParm_map[] fillarray "dB", "log", "lin", "log", "lin", "lin", "lin", "log", "log", "lin", "lin" 

giParm_in ftgen 0, 0, ginum_parms, -2, 0
giParm_out ftgen 0, 0, ginum_parms, -2, 0
giSensors ftgen 0, 0, ginum_sensors, -2, 0
giModscale ftgen 0, 0, ginum_sensors*ginum_parms, -23, "modmatrix.txt"

opcode read_and_map, k,i
index xin
kval table index, giParm_out
if strcmpk(gSParm_map[index],"lin")==0 then
kval = kval*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"log")==0 then
kval = powoftwo(kval*(log2(gkParm_max[index])-log2(gkParm_min[index]))+log2(gkParm_min[index]))
elseif strcmpk(gSParm_map[index],"dB")==0 then
imin_dB = -30
imax_dB = -0
kval = ampdbfs(imin_dB+(kval*(imax_dB-imin_dB)))-ampdbfs(imin_dB)
endif

xout kval
endop

instr 4 ; test
tablew 0.2, 0, giParm_in
tablew 0.2, 1, giParm_in
tablew 0.5, 2, giParm_in
tablew 0.8, 3, giParm_in
tablew 0.3, 4, giParm_in
tablew 0.2, 5, giParm_in
tablew 0.3, 6, giParm_in
tablew 0.7, 7, giParm_in
tablew 0.5, 8, giParm_in
tablew 0.4, 9, giParm_in
endin


instr 5
; modulator mapping, modmatrix processing
kupdate chnget "modmatrix_update"
modmatrix giParm_out, giSensors, giParm_in, giModscale, ginum_sensors, ginum_parms, kupdate
endin


; get k+rate control data, map to parameter data
; initialize parameter values,
; initialize a modmatrix with N control inputs and M parameter outputs
instr 10
endin


; synthesize sound
instr 20

; read from table, scale and map according to mapping type
kamp read_and_map 0
kcps read_and_map 1
kphasedist read_and_map 2
kfilter1fq read_and_map 3
kring read_and_map 4
kpw1 read_and_map 5
kpw2 read_and_map 6
kfilter2fq read_and_map 6
kfilter2res read_and_map 7
kfilter2dist read_and_map 8

#include "submono.inc"

endin

; analyze sound
; output file of k+rate control data 
instr 30
endin



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

giParm_in ftgen 0, 0, ginum_parms, -23, "offsets.txt"
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

; get k+rate control data, map to parameter data in modmatrix
instr 5
kx chnget "x"
ky chnget "y"
kz chnget "z"
tablew kx, 0, giSensors
tablew ky, 1, giSensors
tablew kz, 2, giSensors
endin

instr 10
; modulator mapping, modmatrix processing
kupdate init 1
modmatrix giParm_out, giSensors, giParm_in, giModscale, ginum_sensors, ginum_parms, kupdate
kupdate = 0
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


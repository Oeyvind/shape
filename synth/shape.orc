
sr = 44100
ksmps = 100
nchnls = 2
0dbfs = 1

giSine ftgen 0, 0, 65536, 10, 1
gifftsize 	= 1024
giFftTabSize	= (gifftsize / 2)+1
gifna     	ftgen   1 ,0 ,giFftTabSize, 7, 0, giFftTabSize, 0   	; for pvs analysis
gifnf     	ftgen   2 ,0 ,giFftTabSize, 7, 0, giFftTabSize, 0   	; for pvs analysis

#include "analyze_udos.inc"

; auto rewrite from Python
ginum_parms = 10
ginum_sensors = 1
; auto rewrite end

; generic parameter ranges and mapping, overwritten on selection of active instrument
gSParmnames[] fillarray "amp","cps"," "," "," "," "," "," "," "," "
gkParm_min[] fillarray 0,0,0,0,0,0,0,0,0,0
gkParm_max[] fillarray 1,1,1,1,1,1,1,1,1,1
gSParm_map[] fillarray "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin" 
giParm_values ftgen 0, 0, ginum_parms, -2, 0
chnset giParm_values, "parmvalue_table"

opcode read_and_map, k,i
index xin
kval table index, giParm_values
if strcmpk(gSParm_map[index],"lin")==0 then
kval = kval*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"log")==0 then
kval = powoftwo(kval*(log2(gkParm_max[index])-log2(gkParm_min[index]))+log2(gkParm_min[index]))
elseif strcmpk(gSParm_map[index],"dB")==0 then
imin_dB = -40
imax_dB = -0
kval = ampdbfs(imin_dB+(kval*(imax_dB-imin_dB)))-ampdbfs(imin_dB)
endif

xout kval
endop

; synthesize sound
instr 20
#include "sine.inc"
endin

instr 21
#include "submono.inc"
endin


; analyze sound
instr 30
a1 chnget "a1"
a2 chnget "a2"
a1 = a1+a2*0.5
#include "analysis_parms.inc"
#include "analyze_audio.inc"
#include "analysis_chnset.inc"
endin


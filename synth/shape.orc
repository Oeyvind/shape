
sr = 48000
ksmps = 128
nchnls = 2
0dbfs = 1

#include "/shape/synth/ftables.inc"

gifftsize 	= 1024
gifft_tabsize	= (gifftsize / 2)+1
gifna     	ftgen 1, 0, gifft_tabsize, 2, 0   	; for pvs analysis
gifnf     	ftgen 2, 0, gifft_tabsize, 2, 0   	; for pvs analysis
gianalysis	ftgen 0, 0, 8, 2, 0			; for writing analysis results
chnset gianalysis, "analysis_table"

#include "/shape/synth/analyze_udos.inc"

ginum_parms = 32
; generic parameter ranges and mapping, overwritten on selection of active instrument
gSParmnames[] fillarray "amp","cps"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "
gkParm_min[] fillarray 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
gkParm_max[] fillarray 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
gSParm_map[] fillarray "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin","lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin","lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin","lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin"
giParm_values ftgen 0, 0, ginum_parms, -2, 0
chnset giParm_values, "parmvalue_table"


opcode read_and_map, k,i
index xin
kval table index, giParm_values
kval tonek kval, 10 ; may want to update this if gesture rate changes significantly from the basic 20 Hz we started with
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
#include "/shape/synth/sine.inc"
endin

instr 21
#include "/shape/synth/submono.inc"
endin

instr 22
#include "/shape/synth/additive.inc"
endin

instr 23
#include "/shape/synth/partikkelsynth.inc"
endin

; analyze sound
instr 30
a1 chnget "a1"
a2 chnget "a2"
a1 = a1+a2*0.5
#include "/shape/synth/analysis_parms.inc"
#include "/shape/synth/analyze_audio.inc"
endin

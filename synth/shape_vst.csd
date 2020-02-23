<Cabbage>

form size(401, 415), caption("Shape"), pluginID("shap")
image bounds(0, 0, 401, 214), file("shape.png"), corners(10)

button bounds(20,5,80,10), channel("osc"), text("osc"), colour:0("yellow"), colour:1("green")

button bounds(20,200,80,10), channel("sine"), text("sine") colour:0("yellow"), colour:1("green")
button bounds(110,200,80,10), channel("submono"), text("submono"), colour:0("yellow"), colour:1("green")
button bounds(200,200,80,10), channel("additive"), text("additive"), colour:0("yellow"), colour:1("green")
button bounds(290,200,80,10), channel("partikkel"), text("partikkel"), colour:0("yellow"), colour:1("green")
csoundoutput bounds(0,215,401,200)

</Cabbage>

<CsoundSynthesizer>
<CsOptions>
-dm0 -n
</CsOptions>
<CsInstruments>

;***************************************************
; globals
;***************************************************

	ksmps 	= 128
	nchnls 	= 2
	0dbfs	= 1

#include "ftables.inc"

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
/*
if kval > 1 then
  printks2 "input value above range: %f", kval
elseif kval < 0 then
  printks2 "input value below range: %f", kval
endif
*/
kval tonek kval, 10 ; may want to update this if gesture rate changes significantly from the basic 20 Hz we started with
if strcmpk(gSParm_map[index],"lin")==0 then
  kval = kval*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"log")==0 then
  kval = powoftwo(kval*(log2(gkParm_max[index])-log2(gkParm_min[index]))+log2(gkParm_min[index]))
elseif strcmpk(gSParm_map[index],"sqrt")==0 then
  kval = sqrt(kval)*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"pow2")==0 then
  kval = pow(kval,2)*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"pow3")==0 then
  kval = pow(kval,3)*(gkParm_max[index]-gkParm_min[index])+gkParm_min[index]
elseif strcmpk(gSParm_map[index],"dB")==0 then
  imin_dB = -40
  imax_dB = -0
  kval = ampdbfs(imin_dB+(kval*(imax_dB-imin_dB)))-ampdbfs(imin_dB)
endif

xout kval
endop

gi_osc_handle OSCinit 8101

;gui control
instr 1
kosc chnget "osc"
ksine chnget "sine"
ksubmono chnget "submono"
kadditive chnget "additive"
kpartikkel chnget "partikkel"

kosc_on trigger kosc, 0.5, 0
kosc_off trigger kosc, 0.5, 1
ksine_on trigger ksine, 0.5, 0
ksine_off trigger ksine, 0.5, 1
ksub_on trigger ksubmono, 0.5, 0
ksub_off trigger ksubmono, 0.5, 1
kadd_on trigger kadditive, 0.5, 0
kadd_off trigger kadditive, 0.5, 1
kpar_on trigger kpartikkel, 0.5, 0
kpar_off trigger kpartikkel, 0.5, 1

if kosc_on > 0 then
  event "i", 2, 0, -1
elseif kosc_off > 0 then
  event "i", -2, 0, 0
elseif ksine_on > 0 then
  event "i", 20, 0, -1
elseif ksine_off > 0 then
  event "i", -20, 0, 0
elseif ksub_on > 0 then
  event "i", 21, 0, -1
elseif ksub_off > 0 then
  event "i", -21, 0, 0
elseif kadd_on > 0 then
  event "i", 22, 0, -1
elseif kadd_off > 0 then
  event "i", -22, 0, 0
elseif kpar_on > 0 then
  event "i", 23, 0, -1
elseif kpar_off > 0 then
  event "i", -23, 0, 0
endif
endin

; receive synthesis parameters via OSC
instr 2
k1 init 0
k2 init 0
k3 init 0
k4 init 0
k5 init 0
k6 init 0
k7 init 0
k8 init 0
k9 init 0
k10 init 0
k11 init 0
k12 init 0
k13 init 0
k14 init 0
k15 init 0
k16 init 0
k17 init 0
k18 init 0
k19 init 0
k20 init 0
k21 init 0
k22 init 0
k23 init 0
k24 init 0
k25 init 0

nxt_val:
kk1 OSClisten gi_osc_handle, "/shapesynth", "fffffffffffffffffffffffff", k1,k2,k3,k4,k5,k6,k7,k8,k9,k10,k11,k12,k13,k14,k15,k16,k17,k18,k19,k20,k21,k22,k23,k24,k25
tablew k1, 0, giParm_values
tablew k2, 1, giParm_values
tablew k3, 2, giParm_values
tablew k4, 3, giParm_values
tablew k5, 4, giParm_values
tablew k6, 5, giParm_values
tablew k7, 6, giParm_values
tablew k8, 7, giParm_values
tablew k9, 8, giParm_values
tablew k10, 9, giParm_values
tablew k11, 10, giParm_values
tablew k12, 11, giParm_values
tablew k13, 12, giParm_values
tablew k14, 13, giParm_values
tablew k15, 14, giParm_values
tablew k16, 15, giParm_values
tablew k17, 16, giParm_values
tablew k18, 17, giParm_values
tablew k19, 18, giParm_values
tablew k20, 19, giParm_values
tablew k21, 20, giParm_values
tablew k22, 21, giParm_values
tablew k23, 22, giParm_values
tablew k24, 23, giParm_values
tablew k25, 24, giParm_values

if (kk1 == 0) goto ex_val
  kgoto nxt_val
ex_val:
endin

; synthesize sound
instr 20
#include "sine.inc"
endin

instr 21
#include "submono.inc"
endin

instr 22
#include "additive.inc"
endin

instr 23
#include "partikkelsynth.inc"
endin

</CsInstruments>
<CsScore>
i1 0 86400
</CsScore>

</CsoundSynthesizer>

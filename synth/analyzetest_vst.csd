<Cabbage>
form size(320, 430), caption("Shape analyze test"), pluginID("shan"), colour(40, 50, 55)

checkbox channel("freeze"), bounds(5, 5, 15, 16), colour:0("green"), colour:1("red"), value(0), identchannel("getlatencydisplay")
label bounds(25, 8, 70, 11), text("freeze"), align("left")
hslider channel("amp"), bounds(5, 40, 100, 16), range(0.0, 1.0, 1.0)
label text("amp"), bounds(110, 40, 100, 11), align("left")
hslider channel("env_crest"), bounds(5, 60, 100, 16), range(0.0, 1.0, 1.0)
label text("env_crest"), bounds(110, 60, 100, 11), align("left")
hslider channel("pitch"), bounds(5, 80, 100, 16), range(0.0, 1.0, 1.0)
label text("pitch"), bounds(110, 80, 100, 11), align("left")
hslider channel("centroid"), bounds(5, 100, 100, 16), range(0.0, 1.0, 1.0)
label text("centroid"), bounds(110, 100, 100, 11), align("left")
hslider channel("flatness"), bounds(5, 120, 100, 16), range(0.0, 1.0, 1.0)
label text("flatness"), bounds(110, 120, 100, 11), align("left")
hslider channel("crest"), bounds(5, 140, 100, 16), range(0.0, 1.0, 1.0)
label text("crest"), bounds(110, 140, 100, 11), align("left")
hslider channel("flux"), bounds(5, 160, 100, 16), range(0.0, 1.0, 1.0)
label text("flux"), bounds(110, 160, 100, 11), align("left")
hslider channel("mfccdiff"), bounds(5, 180, 100, 16), range(0.0, 1.0, 1.0)
label text("mfccdiff"), bounds(110, 180, 100, 11), align("left")

csoundoutput bounds(4, 220, 300, 200)
</Cabbage>
<CsoundSynthesizer>
<CsOptions>
</CsOptions>
<CsInstruments>

;sr = 44100  
ksmps = 64
nchnls = 2
0dbfs = 1

gisine ftgen 0, 0, 65536, 10, 1
gifftsize 	= 1024
gifft_tabsize	= (gifftsize / 2)+1
gifna     	ftgen 1, 0, gifft_tabsize, 2, 0   	; for pvs analysis
gifnf     	ftgen 2, 0, gifft_tabsize, 2, 0   	; for pvs analysis
gianalysis	ftgen 0, 0, 8, 2, 0			; for writing analysis results
chnset gianalysis, "analysis_table"

#include "analyze_udos.inc"

; analysis instr
instr 1

a1,a2 ins
a1 = a1+a2*0.5
#include "analysis_parms.inc"
#include "analyze_audio.inc"

kfreeze chnget "freeze"
if kfreeze == 0 then
  chnset krms, "amp"
  chnset kenv_crest1, "env_crest"
  chnset kpitch_n, "pitch"
  chnset kcentroid_n, "centroid"
  chnset kflatness_n, "flatness"
  chnset kcrest_n, "crest"
  chnset kflux_n, "flux"
  chnset kmfccdiff, "mfccdiff"
endif

endin


</CsInstruments>
<CsScore>
i1 0 86400
e
</CsScore>
</CsoundSynthesizer>


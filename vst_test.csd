<CsoundSynthesizer>
<CsOptions>
-m3 --displays -odac
</CsOptions>
<CsInstruments>
sr     = 44100
ksmps  = 20
nchnls = 2

giabsynth vstinit "C:\\Program Files\\Native Instruments\\VSTPlugins 64 bit\\Absynth 5 Stereo.dll", 1
vstinfo giabsynth
vstedit giabsynth

; Send midi notes to the VST
instr 1 
; MIDI channels are numbered starting at 0.
; p3 always contains the duration of the note.
; p4 contains the MIDI key number (pitch),
; p5 contains the MIDI velocity number (loudness),
imidichannel init 0
vstnote giabsynth, imidichannel, p4, p5, p3
endin

; Send parameter changes to the VST
instr 2 
; p4 is the parameter number.
; p5 is the parameter value.
vstparamset giabsynth, p4, p5 
endin

; Send audio from the VST to the output.
instr 3 
a0 init 0
a1, a2 vstaudio giabsynth, a0, a0
outs a1, a2
endin

</CsInstruments>
<CsScore>
i 3 0 -1 ; auddio out
i 1 1 10 60 76
e 12
</CsScore>
</CsoundSynthesizer>
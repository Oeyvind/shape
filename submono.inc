
; limits and smoothing
kphasedist limit (1-kphasedist)*0.5, 0.005, 0.5
kpw1 limit (1-kpw1)*0.5, 0.005, 0.5
kpw2 limit (1-kpw2)*0.5, 0.005, 0.5
kfilter2fq tonek kfilter2fq, 2

; synthesis
imode = 2
avco1 vco2 1, kcps, imode , kpw1
avco1o vco2 1, kcps , imode , kpw1
avco1 = avco1+avco1o
kdet = 0.001*kcps ; VCO2 Detune
avco2 vco2 1, kcps+kdet, imode, kpw2
avco2 = avco2+avco1o
aring = avco1*avco2

aleft = ((avco1)*(1-kring) + aring*kring)
aright = ((avco2)*(1-kring) + aring*kring)
;aleft balance aleft, avco1, 2
;aright balance aright, avco2, 2

aphas vco2 1, kcps, imode, kphasedist

kfilter1fq limit kfilter1fq, 40, 20000
irez = .6 ; VCF Resonance
avcfL moogladder aleft+aphas, kfilter1fq, irez
avcfR moogladder aright+aphas, kfilter1fq, irez

a1 butterhp avcfL*2, kcps * 0.5	; try to filter out some LF artifacts
a2 butterhp avcfR*2, kcps * 0.5	; try to filter out some LF artifacts

amp = interp(kamp)
a1 = a1*amp
a2 = a2*amp

denorm	a1, a2
kfilt limit ((kcps*0.8) + kfilter2fq), 20, 18000
alo lpf18 a1, kfilt, kfilter2res, kfilter2dist
a1 = alo*0.9

alo2 lpf18 a2, kfilt, kfilter2res, kfilter2dist
a2 = alo2*0.9

chnset a1, "a1"
chnset a2, "a2"

outch 1, a1*amp, 2, a2*amp


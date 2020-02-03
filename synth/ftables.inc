; classic waveforms
gisine		ftgen	0, 0, 65536, 10, 1					; sine wave
gicosine	ftgen	0, 0, 8192, 9, 1, 1, 90					; cosine wave
gitri		ftgen	0, 0, 8192, 7, 0, 2048, 1, 4096, -1, 2048, 0		; triangle wave
gipulse		ftgen	0, 0, 1024, 7, 0, 510,0,1,1,1,-1,1,0,510,0					; pulse at middle

gisaw_A		ftgen	0, 0, 65536, 10, 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8,\	; (additive) saw wave
          1/9, 1/10, 1/11, 1/12, 1/13, 1/14,\
          1/15, 1/16, 1/17, 1/18, 1/19, 1/20

gisquare_A	ftgen	0, 0, 65536, 10, 1, 0, 1/3, 0, 1/5, 0, 1/7, 0, 1/9, \	; (additive) square wave
          0, 1/11, 0, 1/13, 0, 1/15, 0, \
          1/17, 0, 1/19

gitriangle_A	ftgen	0, 0, 65536, 9, 1, 1, 0, \				; (additive)triangle wave
          3, 1/(3*3), 180, \
          5, 1/(5*5), 0, \
          7, 1/(7*7), 180, \
          9, 1/(9*9), 0, \
          11, 1/(11*11), 180, \
          13, 1/(13*13), 0, \
          15, 1/(15*15), 180, \
          17, 1/(17*17), 0, \
          19, 1/(19*19), 180

gipulse_A	ftgen	0, 0, 65536, 30, gipulse, 1, 20, sr 		; resynthesize the pulse wave with N harmonics


; grain envelope tables
gisigmorise 	ftgen	0, 0, 8193, 19, 0.5, 1, 270, 1				; rising sigmoid
gisigmofall 	ftgen	0, 0, 8193, 19, 0.5, 1, 90, 1				; falling sigmoid
giexpfall	ftgen	0, 0, 8193, 5, 1, 8193, 0.00001				; exponential decay
gitrianglewin 	ftgen	0, 0, 8193, 7, 0, 4096, 1, 4096, 0			; triangular Window
gisquarewin 	ftgen	0, 0, 8193, 7, 1, 8192, 1			        ; square Window (all on)

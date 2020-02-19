; parameter ranges, mapping
gSParmnames[] fillarray "amp","grainrate", "graindur", "grainsustain", "grainshape", "grfmindx", "fmindx", "fmfeedindx", \
                        "grainfreq", "sinepitch", "sawpitch", "squarepitch", "pulsepitch", \
                        "sineamp", "sawamp", "squareamp", "pulseamp", "trainamp", "sinephase", "sawphase", "squarephase", "pulsephase",\
                        "trainpitch", "trainpartials", "trainchroma"

gkParm_min[] fillarray 0, 50, 0.1, 0.0, 0.01, 0, 0, 0,\
                       0.25,0.25,0.25,0.25,0.25,\
                       0,0,0,0,0,0,0,0,0,\
                       0.25,2,0.25

gkParm_max[] fillarray 1, 1500, 3, 1.0, 0.99, 4, 5, 5,\
                       4,4,4,4,4,\
                       1,1,1,1,1,1,1,1,1,\
                       4,20,3

gSParm_map[] fillarray "dB", "log", "lin", "lin", "lin", "lin", "lin", "lin",\
                       "lin", "lin", "lin", "lin", "lin", \
                       "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", \
                       "lin", "lin", "lin"

; read from table, scale and map according to mapping type
kamp read_and_map 0
kgrainrate read_and_map 1
kgraindur read_and_map 2
ksustain_amount	read_and_map 3
ka_d_ratio read_and_map 4
kGrFmIndex  read_and_map 5
kPtchFmIndex  read_and_map 6
kfeedamt  read_and_map 7
kgrainfreq read_and_map 8
kwavekey1 read_and_map 9
kwavekey2 read_and_map 10
kwavekey3 read_and_map 11
kwavekey4 read_and_map 12
ksineamp read_and_map 13
ksawamp read_and_map 14
ksquareamp read_and_map 15
kpulseamp read_and_map 16
ktrainamp read_and_map 17
ksamplepos1	read_and_map 18
ksamplepos2	read_and_map 19
ksamplepos3	read_and_map 20
ksamplepos4	read_and_map 21
ktrainpitch read_and_map 22
knumpartials read_and_map 23
kchroma read_and_map 24

; synthesis

			  ; select source waveforms 2,3 and 4 (waveform 1 is selected outside of this include file, in the including instrument)
			  kwaveform1	= gisine		; source audio waveform 2
				kwaveform2	= gisaw_A		; source audio waveform 2
				kwaveform3	= gisquare_A		; source audio waveform 3
				kwaveform4	= gipulse_A		; source audio waveform 4

				kphaserate1	= 0
				kphaserate2	= 0
				kphaserate3	= 0
				kphaserate4	= 0

				asamplepos1	phasor kphaserate1
				asamplepos2	phasor kphaserate2
				asamplepos3	phasor kphaserate3
				asamplepos4	phasor kphaserate4

				; mix initial phase and moving phase value
				asamplepos1	= asamplepos1+ksamplepos1
				asamplepos2	= asamplepos2+ksamplepos2
				asamplepos3	= asamplepos3+ksamplepos3
				asamplepos4	= asamplepos4+ksamplepos4

			  ; sync
				async = 0.0					; (disable external sync)

			  ; grain rate FM
				kgrfmdiv = 4
				kGrFmFreq	= divz(kgrainrate,kgrfmdiv,1)				; FM freq for modulating the grainrate
				iGrFmWave	= gisine				; FM waveform, for modulating the grainrate
				aGrFmSig oscil kGrFmIndex, kGrFmFreq, iGrFmWave	; audio signal for frequency modulation of grain rate
				agrainrate = kgrainrate + (aGrFmSig*kgrainrate)	; add the modulator signal to the grain rate signal

			  ; distribution
				kdistribution	= 0.0						; grain random distribution in time
				idisttab ftgentmp	0, 0, 16, 16, 1, 16, -10, 0	; probability distribution for random grain masking

			  ; grain shape
				kduration	= (kgraindur*1000)/kgrainrate		; grain dur in milliseconds, relative to grain rate

				ienv_attack	= gisigmorise 				; grain attack shape (from table)
				ienv_decay = gisigmofall 				; grain decay shape (from table)

				kenv2amt = 0.0					; amount of secondary enveloping per grain (e.g. for fof synthesis)
				ienv2tab = giexpfall 				; secondary grain shape (from table), enveloping the whole grain if used

			  ; grain pitch (transpose, or "playback speed")
				kwavfreq = kgrainfreq*kgrainrate

			  ; pitch sweep
				ksweepshape = 0.5						; grain wave pitch sweep shape (sweep speed), 0.5 is linear sweep
				iwavfreqstarttab ftgentmp	0, 0, 16, -2, 0, 0,   1		; start freq scalers, per grain
				iwavfreqendtab ftgentmp	0, 0, 16, -2, 0, 0,   1		; end freq scalers, per grain

			  ; FM of grain pitch (playback speed)
				kfmratio = 2.5
				kfmratfine = 0
				kPtchFmFreq	= kgrainrate*(kfmratio+kfmratfine)				; FM freq, modulating waveform pitch
				iPtchFmWave	= gisine						; FM waveform, modulating waveform pitch
				ifmamptab	ftgentmp	0, 0, 16, -2, 0, 0,   1			; FM index scalers, per grain
				ifmenv = gisquarewin    					; FM index envelope, over each grain (from table)
				kPtchFmIndex	= kPtchFmIndex + (kPtchFmIndex*kPtchFmFreq*0.00001) 	; FM index scaling formula
				awavfmosc poscil	kPtchFmIndex, kPtchFmFreq, iPtchFmWave		; Modulator signal for frequency modulation inside grain
				afeed init 0
				awavfm = (afeed*kfeedamt) + awavfmosc

  			; trainlet parameters
				icosine = gicosine				; needs to be a cosine wave to create trainlets
				ktraincps	= kgrainrate*ktrainpitch				; set cps equal to grain freq, creating a single cycle of a trainlet inside each grain

			  ; masking
				igainmasks	ftgentmp	0, 0, 16, -2, 0, 0,   1, 0.8, 0.7, 0.6, 0.5, 0.5, 0.4, 0.3

				; channel masking table, output routing for individual grains (zero based, a value of 0.0 routes to output 1)
				ichannelmasks	ftgentmp	0, 0, 16, -2,  0, 0,  0.5

				; random masking (muting) of individual grains
				krandommask	= 0

				; wave mix masking.
				; Set gain per source waveform per grain,
				; in groups of 5 amp values, reflecting source1, source2, source3, source4, and the 5th slot is for trainlet amplitude.
				iwaveamptab	ftgentmp	0, 0, 32, -2, 0, 0,   1,0,0,0,0
				tablew ksineamp, 2, iwaveamptab
				tablew ksawamp, 3, iwaveamptab
				tablew ksquareamp, 4, iwaveamptab
				tablew kpulseamp, 5, iwaveamptab
				tablew ktrainamp, 6, iwaveamptab

  			; system parameter
				imax_grains	= 100				; max number of grains per k-period

a1,a2,a3,a4,a5,a6,a7,a8	partikkel \
		  agrainrate, \
		  kdistribution, idisttab, async, \
			kenv2amt, ienv2tab, ienv_attack, ienv_decay, \
		  ksustain_amount, ka_d_ratio, kduration, \
		  0.25, \
		  igainmasks, \
      kwavfreq, \
			ksweepshape, iwavfreqstarttab, iwavfreqendtab, \
		  awavfm, ifmamptab, ifmenv, \
		  icosine, ktraincps, knumpartials, kchroma, \
		  ichannelmasks, \
		  krandommask, \
		  kwaveform1, kwaveform2, kwaveform3, kwaveform4, \
		  iwaveamptab, \
		  asamplepos1, asamplepos2, asamplepos3, asamplepos4, \
      kwavekey1, kwavekey2, kwavekey3, kwavekey4, \
		  imax_grains

      afeed           = (a1+a2)*0.5
      aenv            madsr 0.001, 0.1, 0.8, 0.1


amp = interp(kamp)
a1 = a1*aenv*amp
a2 = a2*aenv*amp

chnset a1, "a1"
chnset a2, "a2"

outch 1, a1*amp, 2, a2*amp
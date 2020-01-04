;    Copyright 2018 Oeyvind Brandtsegg and Axel Tidemann
;
;    This file is part of the Shape package
;
;    The Shape package is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License version 3 
;    as published by the Free Software Foundation.
;
;    The shape is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with The Feature-Extract-Modulator package.  
;    If not, see <http://www.gnu.org/licenses/>.

; ***************
; pre-emphasis EQ for transient detection,
; allowing better sensitivity to utterances starting with a sibliant.
	kpreEqHiShelfFq	        chnget "preEqHiShelfFq"
	kpreEqHiShelfGain	chnget "preEqHiShelfGain"
	;kpreEqLoShelfFq	        chnget "preEqLoShelfFq"
	;kpreEqLoShelfGain	chnget "preEqLoShelfGain"
	
        a1preEq	                pareq a1, kpreEqHiShelfFq, ampdb(kpreEqHiShelfGain), 0.7,  2
        ;a1preEq	                pareq a1preEq, kpreEqHiShelfFq, ampdb(kpreEqLoShelfGain), 0.7,  1
        ;kautogain               = ampdbfs(-kpreEqHiShelfGain)
        ;a1preEq                 = a1preEq*kautogain
; ***************
; amplitude tracking
	krms_preEq	rms a1preEq			    	; simple level measure (with transient pre emphasis)
	krms_preEq      = krms_preEq*2
	krms		rms a1			    		; simple level measure 
	;krms            = krms*1.4
        krms_dB         = dbfsamp(krms)
                
	kAttack		= 0.001				        ; envelope follower attack
	kRelease        = 0.5;chnget "amp_transientDecTime"           ; envelope follower release
	a_env		follow2	a1preEq, kAttack, kRelease	; envelope follower
        k_env		downsamp a_env	

	knoiseFloor_dB	chnget "inputNoisefloor"
	kgate		= (krms_dB < knoiseFloor_dB ? 0 : 1)	;  gate when below noise floor (for sampholding centroid and pitch etc)
        isecond_dB      = 9
	kgate2		= (krms_dB < knoiseFloor_dB+isecond_dB ? 0 : 1)	;  gate when close to noise floor (for sampholding centroid and pitch etc)
        klowscaler      = limit(dbfsamp(krms)-knoiseFloor_dB, 0, isecond_dB)/isecond_dB      ; scaler to fade out different things towards the noise floor
        krms_dB_n       = (krms_dB/abs(knoiseFloor_dB))+1

        icrestrate      = 4
        kcrestmetro     metro icrestrate
        krms_max        init 0
        krms_max        max krms_max, krms
        krms_max        = (kcrestmetro > 0 ? 0 : krms_max)
        kcrestindex     init 0
        kcrestindex     = (kcrestindex+kcrestmetro)%2
        kcrestArr[]     init 2
        kcrestArr[kcrestindex] = krms_max
        kcrest_max      maxarray kcrestArr ; get max out of N last values
        kenv_crest0     divz kcrest_max, krms, 1
	kcrestrise      = (kgate2 > 0 ? 1 : 10) ; slow response when signal is low
	kcrestfall      = (kgate2 > 0 ? 3 : 8) ; slow response when signal is low
        kcrestA         = 0.001^(1/(kcrestrise*kr))
        kcrestB         = 0.001^(1/(kcrestfall*kr))
        kenv_crest      init 0
        kenv_crest      = (kenv_crest0>kenv_crest?(kenv_crest0+(kcrestA*(kenv_crest-kenv_crest0))):(kenv_crest0+(kcrestB*(kenv_crest-kenv_crest0))))
        kenv_crest1     = (dbamp(kenv_crest))/50



; ***************
;analyze amplitude transients
	iresponse	        = 10 			                ; response time in milliseconds
	ktthresh	        chnget "amp_transientThresh"            ; transient trig threshold 
	klowThresh	        = knoiseFloor_dB                        ; lower threshold for transient detection
        kdoubleLimit            chnget "amp_transientDoubleLimit"       ; minimum duration between events, (double trig limit)
        kdecThresh	        chnget "amp_transientDecThresh"         ; retrig threshold, how much must the level decay from its local max before allowing new transient trig

	krms_tran0, kdiff	TransientDetect dbfsamp(k_env), iresponse, ktthresh, klowThresh, kdecThresh, kdoubleLimit

        ktime           timeinsts
        kprevaTranTime  init 0
        katranDensity   init 0
        
; transient hold, statistics etc 
        ktrigButn       trigger	krms_tran0, 0.5, 0
        if ktrigButn > 0 then
        katranTime      = ktime-kprevaTranTime
        kprevaTranTime  = ktime
        katranDensity_t divz 1, katranTime, 1           ; this will be accurate for slow tempi, but not if you play e.g. two fast consecutive transients followed by a puase
        endif
holdTransient:
        kamp_trans_hold linseg 1,0.05,1,0,0,1,0
rireturn

        katran1second   delayk krms_tran0, 1
        katranCount     init 0
        katranCount     += krms_tran0
        katranCount     -= katran1second                ; this will be accurate when playing an integer number of transient within each period  
                                                        ; but it will have jitter when playing at a tempo of e.g. 3.5 transients per second

        
        katranDensity   = (katranDensity_t < 1 ? katranDensity_t : katranCount)
        katranDensity   = (abs(katranDensity_t-katranCount) < 1 ? katranDensity_t : katranCount)
        iatranrise      = 0.5
	iatrandec       = 4
        itrandensA      = exp(-6.90775527898 * (1/iatranrise)/kr)
        itrandensB      = exp(-6.90775527898 * (1/iatrandec)/kr)
        katransDensEnv  init 0
        katransDensEnv   = (katranDensity>katransDensEnv?(katranDensity+(itrandensA*(katransDensEnv-katranDensity))):(katranDensity+(itrandensB*(katransDensEnv-katranDensity))))
        katransDensEnv_n = katransDensEnv/14
                
        ; transient dynamics
        kenv_dyn_count  init 0
        isize_env_dyn   = 5
        kenv_dyn_Arr[]  init isize_env_dyn
        
        krms_tran0_del delayk krms_tran0, 50/1000
        if krms_tran0 > 0 then
        krms_this       = 0
        endif
        krms_this       max krms, krms_this ; max amp during 50 ms after transient detected
        if krms_tran0_del > 0 then
        kenv_dyn_count  = (kenv_dyn_count+krms_tran0_del)%isize_env_dyn
        kenv_dyn_Arr[kenv_dyn_count] = krms_this
        endif
        kenv_dyn_min5   minarray kenv_dyn_Arr
        kenv_dyn_min2   min kenv_dyn_Arr[kenv_dyn_count], kenv_dyn_Arr[wrap(kenv_dyn_count-1,0,isize_env_dyn-1)]
        kenv_dyn_max5   maxarray kenv_dyn_Arr
        kenv_dyn_max2   max kenv_dyn_Arr[kenv_dyn_count], kenv_dyn_Arr[wrap(kenv_dyn_count-1,0,isize_env_dyn-1)]
        kenv_dyn_min    = (kenv_dyn_min5+kenv_dyn_min2)/2
        kenv_dyn_max    = (kenv_dyn_max5+kenv_dyn_max2)/2
        ;kenv_dyn        limit log10(divz(kenv_dyn_max, kenv_dyn_min, -1))/3, 0, 1
        kenv_dyn        = 1-limit(divz(dbfsamp(kenv_dyn_max)-5, dbfsamp(kenv_dyn_min)-5, -1), 0, 1)


; ***************
; spectral analysis

	iwtype 			= 1
	fsin 			pvsanal	a1, gifftsize, gifftsize/2, gifftsize, iwtype
	kflag   		pvsftw	fsin,gifna,gifnf          	; export  amps  and freqs to table,
        
	kupdateRate		= 200
	kmetro			metro kupdateRate
	kdoflag			init 0
	kdoflag			= (kdoflag + kmetro);*kgate

	; copy pvs data from table to array
	; analyze spectral features
	kArrA[]  		init    gifft_tabsize
	kArrAprev[]  		init    gifft_tabsize
	kArrAnorm[]  		init    gifft_tabsize
	kArrF[]  		init    gifft_tabsize
	kArrCorr[]  		init    gifft_tabsize
	kflatness		init 0

if (kdoflag > 0) && (kflag > 0) then

	kArrAprev[]		= kArrA
        			copyf2array kArrA, gifna
        			copyf2array kArrF, gifnf	
	ksumAmp			sumarray kArrA
	kmaxAmp			maxarray kArrA
	ksumAmp                 = (ksumAmp == 0 ? 1 : ksumAmp)
        kArrAnorm               = kArrA/ksumAmp
        kcentroid               pvscent fsin
	kArrCorr		= kArrA*kArrAprev
	kspread		        = sumarray(((kArrF+(kcentroid*-1))^2)*kArrAnorm)^0.5
	kskewness	        divz sumarray(((kArrF+(kcentroid*-1))^3)*kArrAnorm), kspread^3, 1
	kurtosis	        divz sumarray(((kArrF+(kcentroid*-1))^4)*kArrAnorm), kspread^4, 1	
        kcrest			divz kmaxAmp, ksumAmp/gifft_tabsize, 1  
        kArrAlog[]              = kArrA
        kArrAlog[0]             = 1
        kArrAlog[1]             = 0
        klogmin minarray kArrAlog
        while klogmin == 0 do
        klogmin,klogndx minarray kArrAlog
        kArrAlog[klogndx] = 1
        od
      	kflatness		divz exp(sumarray(log(kArrAlog))/gifft_tabsize),  (ksumAmp/gifft_tabsize), 0
	kflux                   = 1-(divz(sumarray(kArrCorr),(sqrt(sumarray(kArrA^2))*sqrt(sumarray(kArrAprev^2))),0))
	kdoflag 		= 0


; ** filter hack to keep spectral signals at the value analyzed while sound level above noise floor
	kcentroid		samphold kcentroid, kgate
	kcentroid2		samphold kcentroid, kgate2
        kcentroid               = (kgate2 > 0 ? kcentroid : kcentroid2-((kcentroid-kcentroid2)*((1-klowscaler)*0.25)))
	kspread		        samphold kspread, kgate
	kspread2		samphold kspread, kgate2
        kspread                 = (kgate2 > 0 ? kspread : kspread2-((kspread-kspread2)*((1-klowscaler)*0.25)))
	kskewness		samphold kskewness, kgate
	kskewness2		samphold kskewness, kgate2
        kskewness               = (kgate2 > 0 ? kskewness : kskewness2-((kskewness-kskewness2)*((1-klowscaler)*0.25)))
	kurtosis		samphold kurtosis, kgate
	kurtosis2		samphold kurtosis, kgate2
        kurtosis                = (kgate2 > 0 ? kurtosis : kurtosis2-((kurtosis-kurtosis2)*((1-klowscaler)*0.25)))
	kflatness		samphold kflatness, kgate
	kflatness2		samphold kflatness, kgate2
        kflatness               = (kgate2 > 0 ? kflatness : kflatness2-((kflatness-kflatness2)*((1-klowscaler)*0.25)))
	kcrest		        samphold kcrest, kgate
	kcrest2		        samphold kcrest, kgate2
        kcrest                   = (kgate2 > 0 ? kcrest : kcrest2-((kcrest-kcrest2)*((1-klowscaler)*0.25)))
	kflux		        samphold kflux, kgate
	kflux2		        samphold kflux, kgate2
        kflux                   = (kgate2 > 0 ? kflux : kflux2-((kflux-kflux2)*((1-klowscaler)*0.25)))

endif

; post filtering of spectral tracks
        kcentroidf              tonek kcentroid, 20
        kfluxf                  tonek kflux, 20

; ***************
; cepstrum, mfcc

 ibins init gifftsize/2
 kIn[] init gifftsize
 kcnt init 0
 kIn shiftin a1
 kcnt += ksmps
 if kcnt == gifftsize then
  kFFT[] = rfft(kIn)
  kPows[] = pows(kFFT)
  kMFB[] = log(mfb(kPows,300,8000,32))
  kmfcc[] = dct(kMFB)
  kcnt = 0
 endif




; ***************
; pitch tracking
; using four different methods
; ptrack may be better for polyphonic signals
; plltrack probably better for monophonic signals
; pitchamdf is also a good alternative, all depending on the material to be sensed
; pitchtracking based on epoch filtering is effective for vocal signals and speech but may also work ok in other contexts

        kpitchmethod    chnget "pitchmethod"
        kpitch_low      chnget "pitch_low"
        kpitch_high     chnget "pitch_high"
        kpitch_low      init 100
        kpitch_high     init 1000
         
        ; reinit pitchamdf when pitch range changes
        kp_range_change changed kpitch_low, kpitch_high
        if kp_range_change > 0 then
        reinit pamdf
        endif
        
if kpitchmethod == 1 then
	kcps 		init 0	
	ihopsize	= 512
	kcps, ka0 	ptrack a1, ihopsize
        
elseif kpitchmethod == 2 then
	kd 		= 0.1
	kloopf		= 20
	kloopq		= 0.3
	acps, alockp	plltrack a1, kd, kloopf, kloopq, kpitch_low, kpitch_high, ampdbfs(knoiseFloor_dB-8)
	kcps		downsamp acps

elseif kpitchmethod == 3 then
pamdf:
        kcps,k0	        pitchamdf a1, i(kpitch_low), i(kpitch_high), i(kpitch_low), 0 , 1 ,i(kpitch_low) ,0
        rireturn

elseif kpitchmethod == 4 then
	kcps    	EpochCps a1     ; pitch analysis by epoch filtering and zero cross count

endif
	kmedianSize	chnget "pitchFilterSize"
	kcps	        mediank	kcps, kmedianSize, 256
        kcps            limit kcps, kpitch_low, kpitch_high
        kcps            tonek kcps, 50

	kcps		samphold kcps, kgate2
        ksemitone       = limit:k((log2(kcps/440)*12)+69, 0, 127)
        

; ***************
; normalization
        kcps_n          = divz(kcps, kpitch_high, 1)
        kpitch_n        = limit(divz(kcps-kpitch_low, kpitch_high-kpitch_low, 1), 0, 1)    ; normalized and offset
        kcentroid_n     = kcentroidf / (sr*0.15)
        kspread_n       = kspread / (sr*0.15);(sr*0.2)
        kskewness_n     = kskewness / 20
        kurtosis_n      = kurtosis / 250
        kflatness_n     = kflatness * 3
        kcrest_n        = kcrest / 250
        kflux_n         = kfluxf * 4
        ;kautocorr_n     = kautocorr * 2
        imfccscale      = 1/200
        kmax            maxarray kmfcc
        kmin            minarray kmfcc
        kmfcc1          samphold kmfcc[1]*imfccscale, kgate
        kmfcc2          samphold kmfcc[2]*imfccscale, kgate
        kmfcc3          samphold kmfcc[3]*imfccscale, kgate
        kmfcc4          samphold kmfcc[4]*imfccscale, kgate
        kmfcc5          samphold kmfcc[5]*imfccscale, kgate
        kmfcc6          samphold kmfcc[6]*imfccscale, kgate
        kmfccdiff       = (abs((kmfcc1-kmfcc2)*0.5)+
                          abs(kmfcc2-kmfcc3)+
                          abs(kmfcc3-kmfcc4)+
                          abs(kmfcc4-kmfcc5)+
                          abs(kmfcc5-kmfcc6))
        kmfccdiff       mediank kmfccdiff, 60, 60
        kmfccdiff       tonek kmfccdiff, 1

        krms            limit krms, 0, 1
        krms_dB_n       limit krms_dB_n, 0, 1
        krms_preEq      limit krms_preEq, 0, 1
	kenv_crest1	limit kenv_crest1, 0, 1
        kpitch_n        limit kpitch_n, 0, 1
        kcentroid_n     limit kcentroid_n, 0, 1
        kspread_n       limit kspread_n, 0, 1
        kskewness_n     limit kskewness_n, 0, 1
        kurtosis_n      limit kurtosis_n, 0, 1
        kflatness_n     limit kflatness_n, 0, 1
        kcrest_n        limit kcrest_n, 0, 1
        kflux_n         limit kflux_n, 0, 1

        ;kmfcc1          limit kmfcc1, 0, 1
        ;kmfcc2          limit kmfcc2, 0, 1
        ;kmfcc3          limit kmfcc3, 0, 1
        ;kmfcc4          limit kmfcc4, 0, 1
        ;kmfcc5          limit kmfcc5, 0, 1
	kmfccdiff	limit kmfccdiff, 0, 1 

; export analysis to Python
tablew krms, 0, gianalysis
tablew kenv_crest1, 1, gianalysis
tablew kpitch_n, 2, gianalysis
tablew kcentroid_n, 3, gianalysis
tablew kflatness_n, 4, gianalysis
tablew kcrest_n, 5, gianalysis
tablew kflux_n, 6, gianalysis
tablew kmfccdiff, 7, gianalysis


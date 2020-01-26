; parameter ranges, mapping
gSParmnames[] fillarray "amp","cps","amp1","amp2","amp3","amp4","amp5","amp6","amp7","amp8","amp9","amp10","amp11","amp12"
gkParm_min[] fillarray 0, 50, 0,0,0,0,0,0,0,0,0,0,0,0
gkParm_max[] fillarray 1, 5000, 1,1,1,1,1,1,1,1,1,1,1,1
gSParm_map[] fillarray "lin", "log", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin", "lin"

; default values for unmapped parms
tableiw 1, 0, giParm_values
tableiw 0.3, 1, giParm_values
tableiw 0.5, 2, giParm_values
tableiw 0.25, 3, giParm_values
tableiw 0.1, 4, giParm_values
tableiw 0.05, 5, giParm_values
tableiw 0.02, 6, giParm_values
tableiw 0.01, 7, giParm_values
tableiw 0, 8, giParm_values
tableiw 0, 9, giParm_values
tableiw 0, 10, giParm_values
tableiw 0, 11, giParm_values
tableiw 0, 12, giParm_values
tableiw 0, 13, giParm_values

; read from table, scale and map according to mapping type
kamp read_and_map 0
kcps read_and_map 1
kcps tonek kcps, 100
kamp1 read_and_map 2
kamp2 read_and_map 3
kamp3 read_and_map 4
kamp4 read_and_map 5
kamp5 read_and_map 6
kamp6 read_and_map 7
kamp7 read_and_map 8
kamp8 read_and_map 9
kamp9 read_and_map 10
kamp10 read_and_map 11
kamp11 read_and_map 12
kamp12 read_and_map 13


; synthesis
a1 poscil kamp1, kcps
a2 poscil kamp2, kcps*2
a3 poscil kamp3, kcps*3
a4 poscil kamp4, kcps*4
a5 poscil kamp5, kcps*5
a6 poscil kamp6, kcps*6
a7 poscil kamp7, kcps*7
a8 poscil kamp8, kcps*8
a9 poscil kamp9, kcps*9
a10 poscil kamp10, kcps*10
a11 poscil kamp11, kcps*11
a12 poscil kamp12, kcps*12

asum sum a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12
amp = interp(kamp)
a1 = asum*amp*(1/12)
a2 = a1

chnset a1, "a1"
chnset a2, "a2"

outch 1, a1*amp, 2, a2*amp

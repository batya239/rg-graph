#!/usr/bin/python
ri = {
    "r1": "(n+2)/3",
    "r2": "(n+8)/9",
    # "r2": "sympy.numbers.One()",
    "r3": "(5*n+22)/27",
    "r4": "(n*n+6*n+20)/27",
    "r5": "(3*n*n+22*n+56)/81",
    "r6": "(n*n+20*n+60)/81",
    "r7": "(n*n*n+8*n*n+24*n+48)/81",

    "r8": "(2*n**2+55*n+186)/243",
    "r9": "(3*n**3+24*n**2+80*n+136)/243",
    "r10": "(7*n**2+72*n+164)/243",
    "r11": "(11*n**2+76*n+156)/243",
    "r12": "(n**3+10*n**2+72*n+160)/243",
    "r13": "(n**3+14*n**2+76*n+152)/243",
    "r14": "(n**3+18*n**2+80*n+144)/243",
    "r15": "(n**4+10*n**3+40*n**2+80*n+112)/243",

    "r16": "(14*n**2+189*n+526)/729",
    "r17": "(19*n**2+206*n+504)/729",
    "r18": "(n**3+26*n**2+210*n+492)/729",
    "r19": "(n**3+32*n**2+224*n+472)/729",
    "r20": "(n**3+36*n**2+244*n+448)/729",
    "r21": "(n**3+44*n**2+252*n+432)/729",
    "r22": "(3*n**3+38*n**2+224*n+464)/729",
    "r23": "(3*n**3+42*n**2+244*n+440)/729",
    "r24": "(3*n**3+50*n**2+252*n+424)/729",
    "r25": "(5*n**3+56*n**2+252*n+416)/729",
    "r26": "(5*n**3+64*n**2+260*n+400)/729",
    "r27": "(9*n**3+76*n**2+260*n+384)/729",
    "r28": "(n**4+16*n**3+88*n**2+256*n+368)/729",
    "r29": "(n**4+16*n**3+96*n**2+264*n+352)/729",
    "r30": "(n**4+12*n**3+68*n**2+248*n+400)/729",
    "r31": "(n**4+12*n**3+76*n**2+256*n+384)/729",
    "r32": "(3*n**4+30*n**3+120*n**2+256*n+320)/729",

    "r33": "(53*n**2+598*n+1536)/2187",
    "r34": "(n**3+65*n**2+619*n+1502)/2187",
    "r35": "(2*n**3+76*n**2+643*n+1466)/2187",
    "r36": "(2*n**3+87*n**2+674*n+1424)/2187",
    "r37": "(2*n**3+89*n**2+668*n+1428)/2187",
    "r38": "(2*n**3+97*n**2+708*n+1380)/2187",
    "r39": "(3*n**3+78*n**2+630*n+1476)/2187",
    "r40": "(4*n**3+111*n**2+716*n+1356)/2187",
    "r41": "(5*n**3+100*n**2+678*n+1404)/2187",
    "r42": "(5*n**3+110*n**2+712*n+1360)/2187",
    "r43": "(7*n**3+114*n**2+686*n+1380)/2187",
    "r44": "(7*n**3+124*n**2+720*n+1336)/2187",
    "r45": "(7*n**3+136*n**2+748*n+1296)/2187",
    "r46": "(9*n**3+138*n**2+728*n+1312)/2187",
    "r47": "(9*n**3+150*n**2+756*n+1272)/2187",
    "r48": "(9*n**3+158*n**2+796*n+1224)/2187",
    "r49": "(9*n**3+174*n**2+812*n+1192)/2187",
    "r50": "(11*n**3+128*n**2+680*n+1368)/2187",
    "r51": "(11*n**3+148*n**2+748*n+1280)/2187",
    "r52": "(13*n**3+150*n**2+728*n+1296)/2187",
    "r53": "(13*n**3+162*n**2+756*n+1256)/2187",
    "r54": "(13*n**3+170*n**2+796*n+1208)/2187",
    "r55": "(13*n**3+186*n**2+812*n+1176)/2187",
    "r56": "(15*n**3+164*n**2+736*n+1272)/2187",
    "r57": "(17*n**3+182*n**2+796*n+1192)/2187",
    "r58": "(17*n**3+198*n**2+812*n+1160)/2187",
    "r59": "(21*n**3+226*n**2+828*n+1112)/2187",
    "r60": "(29*n**3+250*n**2+828*n+1080)/2187",
    "r61": "(3*n**4+36*n**3+204*n**2+744*n+1200)/2187",
    "r62": "(3*n**4+36*n**3+228*n**2+800*n+1120)/2187",
    "r63": "(3*n**4+40*n**3+232*n**2+760*n+1152)/2187",
    "r64": "(3*n**4+40*n**3+240*n**2+800*n+1104)/2187",
    "r65": "(3*n**4+40*n**3+256*n**2+816*n+1072)/2187",
    "r66": "(3*n**4+44*n**3+268*n**2+816*n+1056)/2187",
    "r67": "(3*n**4+44*n**3+284*n**2+832*n+1024)/2187",
    "r68": "(3*n**4+48*n**3+280*n**2+816*n+1040)/2187",
    "r69": "(3*n**4+52*n**3+308*n**2+832*n+992)/2187",
    "r70": "(5*n**4+62*n**3+304*n**2+808*n+1008)/2187",
    "r71": "(5*n**4+62*n**3+320*n**2+824*n+976)/2187",
    "r72": "(9*n**4+90*n**3+368*n**2+808*n+912)/2187",
    "r73": "(n**4+14*n**3+144*n**2+724*n+1304)/2187",
    "r74": "(n**4+14*n**3+164*n**2+792*n+1216)/2187",
    "r75": "(n**4+14*n**3+180*n**2+808*n+1184)/2187",
    "r76": "(n**4+18*n**3+156*n**2+724*n+1288)/2187",
    "r77": "(n**4+18*n**3+168*n**2+752*n+1248)/2187",
    "r78": "(n**4+18*n**3+176*n**2+792*n+1200)/2187",
    "r79": "(n**4+22*n**3+180*n**2+752*n+1232)/2187",
    "r80": "(n**4+22*n**3+204*n**2+808*n+1152)/2187",
    "r81": "(n**4+26*n**3+196*n**2+740*n+1224)/2187",
    "r82": "(n**4+26*n**3+208*n**2+768*n+1184)/2187",
    "r83": "(n**4+26*n**3+216*n**2+808*n+1136)/2187",
    "r84": "(n**4+26*n**3+232*n**2+824*n+1104)/2187",
    "r85": "(n**4+30*n**3+228*n**2+808*n+1120)/2187",
    "r86": "(n**4+30*n**3+244*n**2+824*n+1088)/2187",
    "r87": "(n**5+14*n**4+84*n**3+312*n**2+784*n+992)/2187",
    "r88": "(n**5+14*n**4+92*n**3+336*n**2+784*n+960)/2187",
    "r89": "(n**5+14*n**4+92*n**3+352*n**2+800*n+928)/2187",
    "r90": "(n**5+18*n**4+120*n**3+400*n**2+784*n+864)/2187",
    "r91": "(n**5+18*n**4+120*n**3+416*n**2+800*n+832)/2187",
    "r92": "(3*n**5+36*n**4+180*n**3+480*n**2+752*n+736)/2187",

    "r93": "(n**5+12*n**4+60*n**3+160*n**2+240*n+256)/729",
     }

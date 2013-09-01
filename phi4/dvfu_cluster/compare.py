# encoding: utf8

## Сравниваю результаты в 5 петлях: мои и Миши

f_mine = open("res.txt")
data1 = eval(f_mine.read())
f_mine.close()

f_mkompan = open("phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py")
data2 = eval(f_mkompan.read())
f_mkompan.close()

for i in data2.keys():
    try:
        delta = abs(data1[i][0] - data2[i][0][0])
        #if delta < 1e-4:
        #    print i,'\t',delta,'\t', data1[i][0],'\t', data2[i][0][0]
    except:
        #pass
        print i

import csv,random,json
from time import strftime,gmtime
val = {}
history = []
for i in range(0,random.randint(0,10)):
    values = [i ** 2 for i in range(0, random.randint(0, 10))]
    val['time'] = strftime("%d-%m-%y  %H:%M", gmtime())
    val['values'] = values
    history.append(json.dumps(val) + "\n")
try:
    with open('test.txt','wb') as file:
        file.writelines(history)
    print val

    with open('test.txt','r') as file:
        for line in file:
            print line

except Exception as e:
    print e

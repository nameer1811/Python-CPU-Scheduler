from random import randint

name = "test" + str(randint(0,1000))
f = open(name,"w")
s = randint(1,20)
p = randint(1,9)
c = randint(1,25)

output = name+" "
output += str(s) +" "
output += str(p) +" "
output += str(c)

for i in range(randint(0,10)):
    i = randint(1,25)
    c = randint(1,25)
    output += " " + str(i) + " "
    output += str(c)

f.write(output)
f.close()
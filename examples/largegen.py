from random import randint

name = "test0"

output = ""

f = open(name,"w")

for i in range(10):
    s = randint(0,20)
    p = randint(0,9)
    c = randint(0,25)

    output += name+" "
    output += str(s) +" "
    output += str(p) +" "
    output += str(c)

    for i in range(randint(0,10)):
        i = randint(0,25)
        c = randint(0,25)
        output += " " + str(i) + " "
        output += str(c)
    output += "\n"
f.write(output)
f.close()
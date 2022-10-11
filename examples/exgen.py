from random import randint

for i in range(100):
    name = "test" + str(i) + "."
    f = open(name,"w")
    s = randint(0,20)
    p = randint(0,9)
    c = randint(0,25)

    output = name+" "
    output += str(s) +" "
    output += str(p) +" "
    output += str(c)

    for i in range(randint(0,10)):
        i = randint(0,25)
        c = randint(0,25)
        output += " " + str(i) + " "
        output += str(c)
    
    f.write(output)
    f.close()
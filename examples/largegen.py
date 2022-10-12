from random import randint, uniform

name = "test0"
max_num = 20

for proc_num in range(0,100):
    name = "test" + str(proc_num)

    output = ""

    f = open(name,"w")

    # different distribution that favors fewer entries
    for i in range(round(uniform(1,max_num**(1/3))**3)):
        s = randint(1,20)
        p = randint(1,9)
        c = randint(1,25)

        output += name+f"_{i}"+" "
        output += str(s) +" "
        output += str(p) +" "
        output += str(c)

        
        for i in range(1,10):
            i = randint(1,25)
            c = randint(1,25)
            output += " " + str(i) + " "
            output += str(c)
        output += "\n"
    f.write(output)
    f.close()
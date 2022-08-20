import time
def timer():
    sec = 0
    min = 0

    timeloop = True
    while timeloop:
        sec += 5
        print(str(min) + " Mins " + str(sec) + " Sec ")
        time.sleep(1)
        if sec == 60:
            sec = 0
            min += 1
        if sec == 30:
            a = 0
            while a < 35:
                a += 5
        elif min == 1 or 2 or 3 or 4 or 5 or 6 or 7:
            a = 0
            while a < 35:
                a += 5

print(timer())




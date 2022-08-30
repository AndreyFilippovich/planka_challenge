import time
def timer(min = 0, sec = 0):
    seven_steps = 0

    timeloop = True
    while timeloop:
        print(str(min) + " Mins " + str(sec) + " Sec ")
        time.sleep(1)

        if sec != 30 and sec != 60:
            sec += 5

        elif sec == 30:
            while seven_steps != 6:
                print(str(min) + " Mins " + str(sec) + " Sec ")
                time.sleep(1)
                seven_steps += 1
                if seven_steps == 6:
                    sec += 5
                continue
         
        if sec == 60:
            sec = 0
            min += 1
            while seven_steps != 0:
                print(str(min) + " Mins " + str(sec) + " Sec ")
                time.sleep(1)
                seven_steps -= 1
                if seven_steps == -1:
                    seven_steps +1
                    sec += 5
                continue

print(timer(1, 5))
def timer(starting_time=0):

    secs = starting_time
    increment = 5
    repeating_step = 0
    repeating_times = 30
    repeating_count = 7 - 1

    while True:
        if repeating_step >= repeating_count or secs % repeating_times != 0:
            secs += increment
            repeating_step = 0
        else:
            repeating_step += 1
        if secs < 60:
            time_text = str(secs) + ' sec.'
        else:
            m, s = divmod(secs, 60)
            time_text = f'{m:02d} min. {s:02d} sec.'
        print(time_text)


timer(5)

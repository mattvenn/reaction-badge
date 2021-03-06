"""
title: reaction timer badge
author: matt venn, 2014
license: GPL attribution share alike
"""
import time
import random
import csv
import threading
import os

csv_file = 'scores.csv'
fade_time = 1.0
max_top_scores = 3
max_bright = 50
high_score_sleep = 30 #show high score every 30s

#undefine for testing with GPIO lib
raspi = True

if raspi:
    import RPi.GPIO as GPIO
    import driver

#interrupt does nothing
def callback(channel):
    pass

if raspi:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    button = 18
    GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def wait_button():
    if raspi:
        #wait for interrupt
        print("wait for button down")
        GPIO.wait_for_edge(button,GPIO.FALLING)
        time_start = time.time()
        GPIO.wait_for_edge(button,GPIO.RISING)
        return time.time() - time_start
    else:
        #wait for key press
        raw_input("press enter key")
        return 0

#write the score
def save_score(score):
    file = open(csv_file,'a')
    writer = csv.writer(file)
    date = time.strftime('%c',time.localtime())
    writer.writerow([date,score])
    file.close()

def get_top_score():
    data = read_file()
    if len(data):
        data.sort(key=lambda x: x[1])
        return data[0][1]
    return 0

#find position in table
def get_pos(score):
    pos = 1
    data = read_file()
    for row in data:
        if score > float(row[1]):
            pos += 1
    return pos

def read_file():
    try:
        file = open(csv_file)
        data = []
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
        return data
    except IOError:
        #return empty array if the file doesn't exist
        return []

#thread for showing high scores
def show_highscores(stop_event):
    top_score = get_top_score()
    short_time = '%.3f' % float(top_score)

    #wait before showing score
    stop_event.wait(5)
    
    while(not stop_event.is_set()):
        #equivalent to time.sleep()
        print(short_time)
        if raspi:
            fade_num(short_time,stop_event.wait)
        stop_event.wait(high_score_sleep)

def shutdown():
    print("shutting down")
    os.system("halt")
    exit(1)


        
#allow passing of a delay func so can be done in high score thread
#and avoid delay after button press
def fade_num(string,delay_func=time.sleep):
    driver.update(string[0])
    driver.fade(0,max_bright,fade_time)
    delay_func(0.5)
    for char in string[1:]:
        if char == '.':
            # hack for now
            char = ' .'
        
        #little pause
        driver.turn_off()
        delay_func(0.2)

        driver.update(char)
        driver.set_pwm(max_bright)
        delay_func(1.1)
    driver.fade(max_bright,0,fade_time)


if __name__ == '__main__':
    try:
        print("starting...")

        #first time init for raspi
        if raspi:
            driver = driver.driver()
            driver.update('P')
            driver.fade(0,max_bright,fade_time)
            driver.fade(max_bright,0,fade_time)
            driver.fade(0,max_bright,fade_time)
            driver.fade(max_bright,0,fade_time)

        while True:
            #create high score thread
            t_stop = threading.Event()
            t = threading.Thread(target=show_highscores, args=(t_stop,))
            t.start()
            #think I need this because the raspi interrupt handler interferes with keyboardinterrupt

            #wait for button to start game
            try:
                l = wait_button()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            #start shutdown thread
            t_stop.set()

            print("waiting for thread to end")
            t.join()
            print("done")
            if l > 5:
                shutdown()
            if raspi:
                driver.update('0')
                driver.fade(max_bright,0,2*fade_time)

            #get a random time to wait
            random_wait = random.randint(3,10)

            #wait it
            for i in range(random_wait):
                time.sleep(1)
                print(".")

            #go!
            print("go!")
            if raspi:
                driver.set_pwm(max_bright)

            start_time = time.time()

            #wait for button
            wait_button()
            reaction_time = time.time() - start_time
            
            if raspi:
                driver.turn_off()

            #work out reaction time and get position in high scores
            if reaction_time < 0.1:
                # something went wrong!
                print("something went wrong")
                if raspi:
                    fade_num('000')
            else:
                short_time = '%.3f' % reaction_time
                pos = get_pos(reaction_time)

                #save high score
                save_score(reaction_time)

                print("you got", short_time)
                print("you came", pos)
                if raspi:
                    fade_num(short_time)
                    time.sleep(0.5)
                    fade_num(str(pos))

    except KeyboardInterrupt:
        print("stopping")
        if t.is_alive():
            print("waiting for thread")
            t_stop.set()
            t.join()
        if raspi:
            driver.cleanup()

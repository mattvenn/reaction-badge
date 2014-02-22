"""
title: reaction timer badge
author: matt venn, 2014
license: GPL attribution share alike
"""
import time
import random
import csv
import threading

csv_file = 'scores.csv'
fade_time = 1.0
max_top_scores = 3
max_bright = 30
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
        GPIO.wait_for_edge(button,GPIO.FALLING)
    else:
        #wait for key press
        raw_input("press enter key")

#write the score
def save_score(score):
    file = open(csv_file,'a')
    writer = csv.writer(file)
    date = time.strftime('%c',time.localtime())
    writer.writerow([date,score])
    file.close()

def get_top_score():
    data = read_file()
    data.sort(key=lambda x: x[1])
    return data[0][1]

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
    short_time = '%.4f' % float(top_score)

    #wait before showing score
    stop_event.wait(5)
    
    while(not stop_event.is_set()):
        #equivalent to time.sleep()
        print(short_time)
        if raspi:
            fade_num(short_time)
        stop_event.wait(high_score_sleep)

def fade_num(string):
    driver.update(string[0])
    driver.fade(0,max_bright,fade_time)
    time.sleep(0.5)
    driver.update(string[1:],True)
    driver.fade(max_bright,0,fade_time)


if __name__ == '__main__':
    try:
        print("starting...")

        #first time init for raspi
        if raspi:
            driver = driver.driver()
            driver.update('0')
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
                wait_button()
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            t_stop.set()

            print("waiting for thread to end")
            t.join()
            print("done")
            if raspi:
                driver.update('0')
                driver.fade(max_bright,0,2*fade_time)

            #get a random time to wait
            random_wait = random.randint(3,10)

            #wait it
            for i in range(random_wait):
                time.sleep(1)
                if raspi:
                    #driver.update(str(i))
                    driver.turn_off()
                    driver.update('0')
                print(".")

            #go!
            print("go!")
            if raspi:
                driver.set_pwm(max_bright)

            start_time = time.time()

            #wait for button
            wait_button()
            
            if raspi:
                driver.turn_off()

            #work out reaction time and get position in high scores
            reaction_time = time.time() - start_time
            short_time = '%.4f' % reaction_time
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

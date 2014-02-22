"""
title: reaction timer badge
author: matt venn, 2014
license: GPL attribution share alike
"""
import time
import random
import csv

csv_file = 'scores.csv'

#undefine for testing with GPIO lib
raspi = False

#interrupt does nothing
def gpio_callback(gpio_id, val):
    pass

if raspi:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    button = 18
    RPIO.add_interrupt_callback(button, gpio_callback, pull_up_down=RPIO.PUD_UP)

def wait_button():
    if raspi:
        #wait for interrupt
        RPIO.wait_for_interrupts()
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

#find position in table
def get_pos(score):
    pos = 1
    data = read_file()
    for row in data:
        print row[1]
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


if __name__ == '__main__':
    while True:
        #wait for button to start game
        wait_button()

        #get a random time to wait
        random_wait = random.randint(3,10)

        #wait it
        for i in range(random_wait):
            time.sleep(1)
            if raspi:
                pass
            else:
                print(".")

        #go!
        if raspi:
            pass
        else:
            print("go!")
        start_time = time.time()

        #wait for button
        wait_button()

        #work out reaction time and get position in high scores
        reaction_time = time.time() - start_time
        short_time = '%.2f' % reaction_time
        pos = get_pos(reaction_time)

        #save high score
        save_score(reaction_time)

        if raspi:
            pass
        else:
            print("you got", short_time)
            print("you came", pos)

"""
title: reaction timer badge
author: matt venn, 2014
license: GPL attribution share alike
"""
import time
import random
import csv
import driver

csv_file = 'scores.csv'

#undefine for testing with GPIO lib
raspi = True

if raspi:
    import RPi.GPIO as GPIO

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

def blink(times=1):
    driver.update('0')
    for i in range(times):
        driver.turn_on()
        time.sleep(0.3)
        driver.turn_off()
        time.sleep(0.3)
    
if __name__ == '__main__':
    while True:
        if raspi:
            blink(2)
        #wait for button to start game
        wait_button()
        if raspi:
            blink(1)
        print("starting...")

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
        if raspi:
            driver.turn_on()

        print("go!")
        start_time = time.time()

        #wait for button
        wait_button()
        
        if raspi:
            driver.turn_off()

        #work out reaction time and get position in high scores
        reaction_time = time.time() - start_time
        short_time = '%.2f' % reaction_time
        pos = get_pos(reaction_time)

        #save high score
        save_score(reaction_time)

        if raspi:
            blink()
            driver.turn_on()
            driver.update(short_time,True)
            driver.turn_off()
            time.sleep(1)
            driver.turn_on()
            driver.update(str(pos),True)

        print("you got", short_time)
        print("you came", pos)

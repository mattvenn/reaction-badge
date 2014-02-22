import time
import random
import csv

csv_file = 'scores.csv'

def wait_button():
    raw_input("press button")

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


while True:
    #wait for button to start game
    wait_button()

    #get a random time to wait
    random_wait = 0 #random.randint(3,10)

    #wait it
    for i in range(random_wait):
        time.sleep(1)
        print(".")

    #go!
    print("go!")
    start_time = time.time()

    wait_button()

    reaction_time = time.time() - start_time
    short_time = '%.2f' % reaction_time
    print("you got", short_time)
    pos = get_pos(reaction_time)
    print("you came", pos)
    save_score(reaction_time)



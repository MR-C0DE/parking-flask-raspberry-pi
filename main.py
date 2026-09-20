import threading
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import time


def nombreAuto():
    fichier = open("data.txt", "r")
    l = fichier.read()
    return l


def entrer():
    fichier = open("data.txt", "r")
    l = fichier.read()
    l = int(l) + 1

    fichier.close()
    fichier1 = open("data.txt", "w")
    fichier1.write(str(l))

    fichier1.close()


def sortir():
    fichier = open("data.txt", "r")
    l = fichier.read()
    if(int(l) > 0):
        l = int(l) - 1

    fichier.close()

    fichier1 = open("data.txt", "w")
    fichier1.write(str(l))

    fichier1.close()


def OpenDoor():

    time.sleep(1)

    kit = ServoKit(channels=16)

    kit.servo[0].angle = 180  # Faire une rotation de 180

    kit.continuous_servo[1].throttle = 1  # ensuite on est a 1

    time.sleep(1)

    kit.continuous_servo[1].throttle = -1  # On remet a 1

    time.sleep(1)

    kit.servo[0].angle = 0  # On tourne a l angle 0

    kit.continuous_servo[1].throttle = 0


# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)


def distance(GPIO_TRIGGER, GPIO_ECHO):
    # set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting ", self.name)
        # Get lock to synchronize threads
        threadLock.acquire()
        print_time(self.name, self.counter, 3)
        try:
            while True:
                print('IL Y A ', nombreAuto(),
                      ' NOMBRE(S) DE VOITURE DANS LE PARKING')
                dist_gauche = distance(19, 16)
                dist_droite = distance(21, 20)

                if dist_gauche <= 4 or dist_droite <= 4:
                    print('Opening')
                    if dist_gauche <= 4:
                        print('Une voiture vient de sortir')
                        sortir()
                    elif dist_droite <= 4:
                        print('Une voiture vient d\'entrer')
                        entrer()
                    OpenDoor()
                else:
                    print('Closing')
                #print("La distance A est de : %.1f cm" % dist_gauche)
                #print("La distance B est de : %.1f cm" % dist_droite)
                time.sleep(1)

            # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("L'utilisateur vient de stoper la mesure de la distance")
            GPIO.cleanup()
        # Free lock to release next thread
        threadLock.release()


def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


if __name__ == '__main__':

    threadLock = threading.Lock()
    threads = []

    # Create new threads
    thread1 = myThread(1, "Thread-1", 1)
    thread2 = myThread(2, "Thread-2", 2)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print("Exiting Main Thread")

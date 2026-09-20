import threading
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import time

class ParkingSystem:
    def __init__(self):
        self.threadLock = threading.Lock()
        self.threads = []

        # GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

    def distance(self, GPIO_TRIGGER, GPIO_ECHO):
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

    def OpenDoor(self):
        time.sleep(1)

        kit = ServoKit(channels=16)

        kit.servo[0].angle = 180  # Faire une rotation de 180

        kit.continuous_servo[1].throttle = 1  # ensuite on est à 1

        time.sleep(1)

        kit.continuous_servo[1].throttle = -1  # On remet à 1

        time.sleep(1)

        kit.servo[0].angle = 0  # On tourne à l'angle 0

        kit.continuous_servo[1].throttle = 0

    def nombreAuto(self):
        fichier = open("data.txt", "r")
        l = fichier.read()
        return l

    def entrer(self):
        fichier = open("data.txt", "r")
        l = fichier.read()
        l = int(l) + 1

        fichier.close()
        fichier1 = open("data.txt", "w")
        fichier1.write(str(l))

        fichier1.close()

    def sortir(self):
        fichier = open("data.txt", "r")
        l = fichier.read()
        if int(l) > 0:
            l = int(l) - 1

        fichier.close()

        fichier1 = open("data.txt", "w")
        fichier1.write(str(l))

        fichier1.close()

    def parking_thread(self, threadID, name, counter):
        print("Starting ", name)
        threadLock = self.threadLock
        try:
            while True:
                print('IL Y A ', self.nombreAuto(), ' NOMBRE(S) DE VOITURE DANS LE PARKING')
                dist_gauche = self.distance(19, 16)
                dist_droite = self.distance(21, 20)

                if dist_gauche <= 4 or dist_droite <= 4:
                    print('Opening')
                    if dist_gauche <= 4:
                        print('Une voiture vient de sortir')
                        self.sortir()
                    elif dist_droite <= 4:
                        print('Une voiture vient d\'entrer')
                        self.entrer()
                    self.OpenDoor()
                else:
                    print('Closing')
                time.sleep(1)

        except KeyboardInterrupt:
            print("L'utilisateur vient de stoper la mesure de la distance")
            GPIO.cleanup()

if __name__ == '__main__':
    parking_system = ParkingSystem()

    # Create new threads
    thread1 = threading.Thread(target=parking_system.parking_thread, args=(1, "Thread-1", 1))
    thread2 = threading.Thread(target=parking_system.parking_thread, args=(2, "Thread-2", 2))

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    parking_system.threads.append(thread1)
    parking_system.threads.append(thread2)

    # Wait for all threads to complete
    for t in parking_system.threads:
        t.join()
    print("Exiting Main Thread")

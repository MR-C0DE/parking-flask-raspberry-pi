
import threading
from threading import Thread
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from flask import Flask, render_template, Response, request, jsonify
import time
from datetime import datetime
import func


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('boards.html')



# Route SSE pour envoyer les mises à jour en temps réel
@app.route('/source')
def source():
    def event_stream():
        while True:
            # Lisez la valeur depuis le fichier ou une autre source en temps réel
            with open('source.txt', 'r') as file:
                value = file.read()

            yield f"data: {value}\n\n"
            time.sleep(1)  # Attendez une seconde avant de vérifier à nouveau le fichier

    return Response(event_stream(), content_type='text/event-stream')




# Route SSE pour envoyer les mises à jour en temps réel
@app.route('/nombre')
def nombre():
    def event_stream():
        while True:
            # Lisez la valeur depuis le fichier ou une autre source en temps réel
            with open('data.txt', 'r') as file:
                value = file.read()

            yield f"data: {value}\n\n"
            time.sleep(1)  # Attendez une seconde avant de vérifier à nouveau le fichier

    return Response(event_stream(), content_type='text/event-stream')





# Route SSE pour envoyer les mises à jour en temps réel
@app.route('/state')
def stream():
    def event_stream():
        while True:
            # Lisez la valeur depuis le fichier ou une autre source en temps réel
            with open('state.txt', 'r') as file:
                value = file.read()

            yield f"data: {value}\n\n"
            time.sleep(1)  # Attendez une seconde avant de vérifier à nouveau le fichier

    return Response(event_stream(), content_type='text/event-stream')


# Route SSE pour envoyer les mises à jour en temps réel
@app.route('/raison')
def raison():
    def event_stream():
        while True:
            # Lisez la valeur depuis le fichier ou une autre source en temps réel
            with open('raison.txt', 'r') as file:
                value = file.read()

            yield f"data: {value}\n\n"
            time.sleep(1)  # Attendez une seconde avant de vérifier à nouveau le fichier

    return Response(event_stream(), content_type='text/event-stream')




@app.route('/datetime')
def dateTime():
    def event_stream():
        while True:
            current_time = datetime.now().strftime('%H:%M:%S')
            yield f"data: {current_time}\n\n"
            time.sleep(1)  # Attendez une seconde avant d'envoyer la prochaine mise à jour

    return Response(event_stream(), content_type='text/event-stream')








@app.route('/update', methods=['POST'])
def update():

    CloseDoor()
    data = request.get_json()
    new_value = data.get('newValue', '')

    file = open("state.txt", "w")
    file.write(str(new_value))

    file.close()
    fichier1 = open("raison.txt", "w")
    fichier1.write("N/A")

    fichier1.close()

    return jsonify({'message': 'Valeur mise à jour avec succès'})

@app.route('/updateOpen', methods=['POST'])
def updateOpen():

    data = request.get_json()
    new_value = data.get('newValue', '')
    raison = data.get('raison', '')
    OpenDoor()
    if raison == "entrer":
        func.incrementer_compteur()
    elif raison == "sortir":
        func.decrementer_compteur()
    else:
        func.raison_inconnue()

    func.modification_etat(new_value)
    return jsonify({'message': 'Valeur mise à jour avec succès'})

# Fonction pour un minuteur simple
def minuteur():
    for i in range(1, 6):
        print(f"Minuteur: {i} minute(s)")
        time.sleep(60)
        







temps_porte_ouverte = 0


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

    kit.servo[0].angle = 90  # Faire une rotation de 180

    kit.continuous_servo[1].throttle = 1  # ensuite on est a 1

    time.sleep(1)

    kit.continuous_servo[1].throttle = -1  # On remet a 1
    func.modification_etat('open')


def CloseDoor():
    global temps_porte_ouverte
    time.sleep(1)
    kit = ServoKit(channels=16)
    kit.servo[0].angle = 10  # On tourne a l angle 0

    kit.continuous_servo[1].throttle = 0
    func.modification_etat('close')
    temps_porte_ouverte = 0

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

def event_servo (dist_gauche, dist_droite):
    global temps_porte_ouverte
    print("NOMBRE DES VOITURES DANS LE PARKING : ", func.lire_compteur())
    print("distance droite : ", dist_gauche, " - distance gauche : ", dist_droite, " :: ", func.lire_etat(), func.lire_capteur())
    time.sleep(2)
    if func.lire_etat() == 'close':
        if dist_gauche <= 4 or dist_droite <= 4:
            OpenDoor()
            temps_porte_ouverte = 0;
            if dist_gauche <= 4:
                func.modification_capteur("g")
                print('Une voiture veut sortir')
                        
            elif dist_droite <= 4:
                func.modification_capteur("d")
                print('Une voiture veut entrer')
        
        
            
    if func.lire_etat() == 'open':
        temps_porte_ouverte += 1
        print("La porte est actuellement ouverte", temps_porte_ouverte)
        if func.lire_capteur() == "g" and dist_droite <= 4:    
            CloseDoor()
            func.decrementer_compteur()
            
        elif func.lire_capteur() == "d" and dist_gauche <= 4:    
            CloseDoor()
            func.incrementer_compteur()
            
        if  temps_porte_ouverte >= 30 and (dist_gauche > 4 and dist_droite > 4):
            print("La porte est restée ouverte pendant au moins 30 secondes et le capteur détecte une valeur supérieure à 4")
            temps_porte_ouverte = 0
            CloseDoor()

            
def run_servo():
    try:
        while True:

            dist_gauche = distance(19, 16)
            dist_droite = distance(21, 20)
            event_servo (dist_gauche, dist_droite)

    except KeyboardInterrupt:
        print("L'utilisateur a arrêté la mesure de la distance")
        GPIO.cleanup()


class MonThread(Thread):
    def __init__(self, task, *args, **kwargs):
        super(MonThread, self).__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.task(*self.args, **self.kwargs)

# Création des instances de la classe Thread pour chaque fonction
thread_flask = MonThread(task=app.run)
thread_minuteur = MonThread(task=run_servo)

# Démarrage des threads
thread_flask.start()
time.sleep(2)
thread_minuteur.start()

# Attente que les threads se terminent (optionnel)
thread_flask.join()
thread_minuteur.join()



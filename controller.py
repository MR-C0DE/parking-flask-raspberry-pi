#from Hardware import controller
from flask import Flask, render_template, request
import datetime
import Servo
import System
import main
from threading import Thread, Lock
host_name = "0.0.0.0"
port = 5000
app = Flask(__name__)
etat = 'ferme'
lastOpened = ''

@app.route('/')
def DataEntry():
    print("Acceuil")
    return render_template('index.html')

@app.route('/result',methods = ['POST'])
def update():
    global etat
    print("Etat porte: ", etat)

    etat = 'Ouverte'
    result = request.form
    Servo.OpenDoor()
    etat = 'ferme'
    
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    lastOpened = 'Last opened : '+timeString
    templateData = {
      'title' : 'HELLO!',
      'time': timeString,
      'etat': etat+lastOpened,
      'items': System.CounterItems
      } 
    
    return render_template('index.html', **templateData)

@app.route('/result', methods = ['GET'])
def result():
    global etat
    print("Etat porte: ", etat)
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
      'title' : 'HELLO!',
      'time': timeString,
      'etat': etat+lastOpened,
      'items': System.CounterItems
      } 
    return render_template('index.html', **templateData)

if __name__ == '__main__':
    
    # Create new threads
    
    #threadGate = System.myThread(1, "Gate Thread", main.ManageGate)
    #threadFlask = System.myThread(2, "Flask Thread", app.run(debug=False, host='0.0.0.0'))
    #threadManageDoor = System.myThread(3, "Door Thread", main.ManageDoor)
    threadGate = Thread(target=main.ManageGate, name='Gate Thread')
    threadFlask = Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()
    # Start new Threads
    threadGate.start()
    #threadFlask.start()
    #threadManageDoor.start()

    # Add threads to thread list
    System.threads.append(threadGate)
    System.threads.append(threadFlask)

    # Wait for all threads to complete
    for t in System.threads:
        t.join()
    print ("Exiting Main Thread")
    
    #threadInsideSensor.start()
    #threadOutsideSensor.start()
    #Servo.OpenDoor()
    

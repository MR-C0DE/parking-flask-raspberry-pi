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

    if raison == "entrer":
        func.incrementer_compteur()
    elif raison == "sortir":
        func.decrementer_compteur()
    else:
        func.raison_inconnue()

    func.modification_etat(new_value)
    return jsonify({'message': 'Valeur mise à jour avec succès'})


if __name__ == '__main__':
    app.run(debug=True)

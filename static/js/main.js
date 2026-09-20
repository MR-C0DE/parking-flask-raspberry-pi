const valueElement = document.getElementById("source");

// Écoute des Server-Sent Events depuis le serveur
const eventSource = new EventSource("/source");

// Fonction pour mettre à jour la valeur sur la page
eventSource.onmessage = function (event) {
  valueElement.innerHTML = event.data;
};

// Écoute des Server-Sent Events depuis le serveur
const eventState = new EventSource("/state");

// Fonction pour mettre à jour la valeur sur la page
eventState.onmessage = function (event) {
  const portes = document.querySelectorAll(".porte");
  const btn_operation = document.querySelector("#operating-btn");
  if (event.data === "open") {
    portes[0].setAttribute("class", "porte porte-ouvert");
    portes[1].setAttribute("class", "porte");
    btn_operation.setAttribute("class", "btn-fermer");
    btn_operation.textContent = "Fermer";
  } else if (event.data === "close") {
    portes[0].setAttribute("class", "porte");
    portes[1].setAttribute("class", "porte porte-fermer");
    btn_operation.setAttribute("class", "btn-ouvrir");
    btn_operation.textContent = "Ouvrir";
  } else {
    portes[0].setAttribute("class", "porte");
    portes[1].setAttribute("class", "porte");
    btn_operation.setAttribute("class", "null");
    btn_operation.textContent = "Inconnue";
  }
};

// Écoute des Server-Sent Events depuis le serveur
const eventTime = new EventSource("/datetime");

// Fonction pour mettre à jour la valeur sur la page
eventTime.onmessage = function (event) {
  document.querySelector("#time").innerText = event.data;
};

// Écoute des Server-Sent Events depuis le serveur
const eventNombre = new EventSource("/nombre");

// Fonction pour mettre à jour la valeur sur la page
eventNombre.onmessage = function (event) {
  document.querySelector("#nbr").innerText = event.data;
};

// Écoute des Server-Sent Events depuis le serveur
const eventRaison = new EventSource("/raison");

// Fonction pour mettre à jour la valeur sur la page
eventRaison.onmessage = function (event) {
  document.querySelector("#because").innerText = event.data;
};


document.querySelector("footer button").addEventListener("click", (event) => {
  event.preventDefault();
  const data = { Ouvrir: "open", Fermer: "close", Inconnue: "close" };
  const newValue = data[event.target.textContent];

  if(newValue === 'open'){
    document.querySelector('.raison').style.display = "block";
    return;
  }

  // Envoi de la nouvelle valeur au serveur via une requête POST
  fetch("/update", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ newValue }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Réponse du serveur :", data);
    })
    .catch((error) => {
      console.error("Erreur lors de la mise à jour de la valeur :", error);
    });
});



const raisonBtns = document.querySelectorAll(".raison div button");

raisonBtns[0].addEventListener("click", ()=>{
  document.querySelector('.raison').style.display="none";
});

raisonBtns[1].addEventListener("click", ()=>{

  const radios = document.querySelectorAll('input[type="radio"]');
  let raison = null;

 


  radios.forEach(radio => {
    if( radio.checked){
      raison = radio.value;
    }
  });

  const data = {
    newValue: "open",
    raison
  }

  fetch("/updateOpen", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify( data ),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Réponse du serveur :", data);
    })
    .catch((error) => {
      console.error("Erreur lors de la mise à jour de la valeur :", error);
    });

  document.querySelector('.raison').style.display="none";
});

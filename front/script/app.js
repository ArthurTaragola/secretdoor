const IP = window.location.hostname + 'http://169.254.10.1:5000';
const socket = io.connect('http://169.254.10.1:5000');

//#region ***********  socket   ***********

const knop = function () {
    socket.emit('knop', {'value': true});
};


//#endregion

//#region ***********  Callback - HTML Generation (After select) ***********
// show________

//#endregion

//#region ***********  Callback - (After update/delete/insert) ***********
// callback______

const callback_gebruikers = function(data)
{
  console.log(data);
  let optionsHTML = '';
  for (const gebruiker of data) {
      optionsHTML += `<option value="${gebruiker.Voornaam}">${gebruiker.Voornaam}</option>`;
  }
  domGebruiker.innerHTML = optionsHTML;
};

const callback_sensoren = function(data)
{
  console.log(data);
  let optionsHTML = '';
  for (const sensor of data) {
      optionsHTML += `<option value="${sensor.Naam}">${sensor.Naam}</option>`;
  }
  domSensor.innerHTML = optionsHTML;
};

const callback_metingen = function(data)
{
  console.log(data);
  let optionsHTML = '';
  for (const meting of data) {
      optionsHTML += `<option value="${meting.waarde}">${meting.waarde} op tijdstip: ${meting.tijdstip}</option>`;
  }
  domMeting.innerHTML = optionsHTML;
};

//#endregion
//#region ***********  Data Access ***********
// get_______

//#endregion

//#region ***********  Event Listeners ***********
// listenTo________________


//#endregion //inladen van de data


const getgebruikers = function() {
  let link;
  link = `http://169.254.10.1:5000/api/v1/gebruikers`;
  handleData(link, callback_gebruikers);
}

const getsensoren = function() {
  let link;
  link = `http://169.254.10.1:5000/api/v1/sensoren`;
  handleData(link, callback_sensoren);
}

const getmetingen = function() {
  let link;
  link = `http://169.254.10.1:5000/api/v1/metingen`;
  handleData(link, callback_metingen);
}


//#region ***********  INIT / DOMContentLoaded ***********
const init = function() {
  // Get some DOM, we created empty earlier.
  domGebruiker = document.querySelector('.js-gebruikers');
  domSensor = document.querySelector('.js-sensoren');
  domMeting = document.querySelector('.js-metingen');
  getgebruikers();
  getmetingen();
  getsensoren();

  socket.on('connected', function (data) {
    toggleValue = data.value;
});
document.querySelector('.power').addEventListener('click', knop);
};


document.addEventListener('DOMContentLoaded', init);
//#endregion

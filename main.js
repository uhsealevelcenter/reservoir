URL_pre = "https://uhslc.soest.hawaii.edu/reservoir/";
DEF_STATION = "EDD024F8";
const qq = window.location.search;
const urlParams = new URLSearchParams(qq);
var mean;
var stdev;
var isGMT, currentStation, currentStationName;


var disclaimerContent = 'The data provided on this web site is subject to continual updating. The University of Hawaii Sea Level Center (UHSLC) and the Hawaii Department of Land and Natural Resources (DLNR) does not guarantee the accuracy, completeness, timeliness, or correct sequencing of the data and information provided in this web site. <br>' +
  '<br> UHSLC and DLNR assumes no responsibility arising from the use, accuracy, completeness, and timeliness of any information, product, or process contained in this web site.<br>' +
  '<br> Viewers/Users are responsible for verifying the accuracy of the information and agree to indemnify UHSCL and DLNR, its officers and employees from any liability, which may arise from the use of its data or information.<br>' +
  '<br> Click Accept if you understand and accept the Terms of Use of this web site and data, otherwise click Cancel to EXIT.';

vers = urlParams.get('v');

$(document).ready(function() {

  createAndOpenModal();

  if (vers == "full")
    v = "-full"
  else v = ""

  isGMT = !$('#timeToggle').prop("checked");
  currentStation = DEF_STATION;
  currentStationName = "Nuuanu";
  $('#selectbox').load(URL_pre + 'selectbox.html', function() {
    $('.select2').val(DEF_STATION).trigger('change');

    makeplot(DEF_STATION, "Nuuanu", isGMT);
    $('#selectbox').on('select2:select', function(e) {
      console.log("SELECT@ CHANGRD");
      var data = e.params.data;
      var stn = data.id + v;
      var stn_name = data.text.substr(17, data.text.length);
      currentStation = stn;
      currentStationName = stn_name;
      makeplot(stn, stn_name, isGMT);
    });
  });

});

$("#timeToggle").off().on('change', function() {
  isGMT = !$('#timeToggle').prop("checked");
  console.log("IS GMT time after change? " + isGMT);
  makeplot(currentStation, currentStationName, isGMT);
  // updateTime($('#timeToggle').prop("checked"));
});

function createAndOpenModal() {
  var myModal = new jBox('Confirm', {
    content: disclaimerContent,
    title: '<h2>Disclaimer</h2>',
    confirmButton: 'Accept',
    cancelButton: 'Cancel',
    cancel: onPopUpCancel,
    confirm: onPopUpConfirm
  });

  myModal.open();
}

function onPopUpCancel() {
  console.log("CANCELED");
// As per: https://stackoverflow.com/questions/19851782/how-to-open-a-url-in-a-new-tab-using-javascript-or-jquery
  var win = window.open('https://dlnreng.hawaii.gov/fcds/', '_self');
  if (win) {
    //Browser has allowed it to be opened
    win.focus();
  } else {
    //Browser has blocked it
    alert('Please allow popups for this website');
  }
}

function onPopUpConfirm() {
  console.log("CONFIRMED");
}

// In case we do not want to use Jquery
// var callback = function(){
//   // Handler when the DOM is fully loaded
//   console.log("DOM LOADED");
// };
//
// if (
//     document.readyState === "complete" ||
//     (document.readyState !== "loading" && !document.documentElement.doScroll)
// ) {
//   callback();
// } else {
//   document.addEventListener("DOMContentLoaded", callback);
// }

URL_pre="https://uhslc.soest.hawaii.edu/reservoir/";
DEF_STATION = "EDD024F8";
var mean;
var stdev;
var isGMT, currentStation, currentStationName;

$(document).ready(function() {
  isGMT = !$('#timeToggle').prop("checked");
  currentStation = DEF_STATION;
  currentStationName = "Nuuanu";
$('#selectbox').load(URL_pre + 'selectbox.html', function() {
  $('.select2').val(DEF_STATION).trigger('change');

  makeplot(DEF_STATION, "Nuuanu", isGMT);
  $('#selectbox').on('select2:select', function(e) {
    console.log("SELECT@ CHANGRD");
      var data = e.params.data;
      var stn = data.id;
      var stn_name = data.text.substr(17,data.text.length);
      currentStation = stn;
      currentStationName = stn_name;
        makeplot(stn, stn_name, isGMT);
    });
});

});

$("#timeToggle").off().on('change', function() {
  isGMT = !$('#timeToggle').prop("checked");
  console.log("IS GMT time after change? "+isGMT);
  makeplot(currentStation, currentStationName, isGMT);
  // updateTime($('#timeToggle').prop("checked"));
});






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

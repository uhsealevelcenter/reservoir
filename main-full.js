URL_pre="https://uhslc.soest.hawaii.edu/reservoir/";
DEF_STATION = "EDD024F8";

$(document).ready(function() {
$('#selectbox').load(URL_pre + 'selectbox.html', function() {
  $('.select2').val(DEF_STATION).trigger('change');

  makeplot(DEF_STATION, "Nuuanu");
  $('#selectbox').on('select2:select', function(e) {
      var data = e.params.data;
      var stn = data.id + '-full';
      var stn_name = data.text.split(" ")[2];
        makeplot(stn, stn_name);
    });
});

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

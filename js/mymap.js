var map = L.map('map',{
}).setView([21.102, -157.327], 7);
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
  maxZoom: 18,
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
    '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
    'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  id: 'mapbox/light-v9',
  tileSize: 512,
  zoomOffset: -1
}).addTo(map);



//Loading stations locations
var mainGeoJSON = new L.GeoJSON.AJAX("stations.geojson");

var stationPointsLayer = {};
mainGeoJSON.on('data:loaded', function() {
  console.log("Loaded", mainGeoJSON);
  var geoJsonFormat = this.toGeoJSON();

  stationPointsLayer = L.geoJSON(geoJsonFormat, {
  // filter: function(feature, layer) {
  //   return typeof feature.properties.sl_component !== "undefined";
  // }
});

stationPointsLayer.addTo(map);

});

mainGeoJSON.on('data:progress', function() {
  console.log("Progress");
});

mainGeoJSON.on('data:loading', function() {
  console.log("Loading");
});

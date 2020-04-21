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
    onEachFeature: onEachFeature
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


function onEachFeature(feature, layer) {
  layer.on({
    mouseover: highlightFeature,
    // mouseout: resetHighlight,
    click: zoomToFeature
  });
}

function highlightFeature(e) {
  var layer = e.target;
  //
  // layer.setStyle({
  //   weight: 5,
  //   color: '#666',
  //   // fillColor: '#fd6f53',
  //   dashArray: '',
  //   fillOpacity: 0.7
  // });
  //
  // if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
  //   // layer.bringToFront();
  // }

  info.update(layer.feature.properties);
}

function zoomToFeature(e) {

  var stationID = e.target.feature.id;
  $('.select2').val(stationID);
  $('.select2').trigger('change'); // Notify any JS components that the value changed
  map.setView([e.target.feature.geometry.coordinates[1],e.target.feature.geometry.coordinates[0]], 12)
  currentStation = stationID;
  currentStationName = e.target.feature.properties.name;
  makeplot(stationID, currentStationName, isGMT);
}


// control that station name on hover
var info = L.control();

info.onAdd = function (map) {
  this._div = L.DomUtil.create('div', 'info');
  this.update();
  return this._div;
};

info.update = function (props) {

  this._div.innerHTML = '<h4>DLNR stations:</h4>' +  (props ?
    '<b>' + props.name + '</b><br />' : 'Hover over a station');
};

info.addTo(map);

function focusOnMapObject(objID) {
  stationPointsLayer.eachLayer(function(l){
      if(l.feature.id == objID){
        info.update(l.feature.properties);
        map.setView([l.feature.geometry.coordinates[1],l.feature.geometry.coordinates[0]], 12)
      }
    });

}

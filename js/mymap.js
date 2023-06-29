var GREY = "#aaaaaa";
var RED = "#FF310D";

var map = L.map('map',{
}).setView([21.102, -157.327], 7);
L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: 'Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
  tileSize: 512,
  zoomOffset: -1
}).addTo(map);


var markers = [];
var regionAlertLayer = {};
var allPulsesGroup = {};

//Loading stations locations
var mainGeoJSON = new L.GeoJSON.AJAX("stations.geojson");

var stationPointsLayer = {};
mainGeoJSON.on('data:loaded', function() {
  // console.log("Loaded", mainGeoJSON);
  var geoJsonFormat = this.toGeoJSON();

  stationPointsLayer = L.geoJSON(geoJsonFormat, {
    onEachFeature: onEachFeature
  // filter: function(feature, layer) {
  //   return typeof feature.properties.sl_component !== "undefined";
  // }
});



regionAlertLayer = L.geoJSON(geoJsonFormat, {

  pointToLayer: function(feature, latlng) {

    if (feature.properties.level_alert>0) {
      var alertColor = {};
      switch (feature.properties.level_alert) {
        // case 0:
        //   alertColor = GREY;
        //   break;
        case 1:
          alertColor = RED;
          break;
      }
      // create a pulse icon
      var pulse = L.icon.pulse({
        iconSize: [20, 20],
        color: alertColor,
        fillColor: alertColor,
      });
      // Create a marker at lat,lng that has pulse icon
      var mark = new L.marker(latlng, {
        icon: pulse,
        title: feature.properties.name,
        myCustomOption: "Can Insert Data Here",
      });
      // Added all markers to the markers an array that is added to a Layer to be
      // displayed below
      markers.push(mark);
    }
    // return L.circleMarker(latlng, geojsonMarkerOptions);
  }
});

allPulsesGroup = L.layerGroup(markers);
// allPulsesGroup.addTo(map);

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
  //$('.select2').val(stationID);
  //$('.select2').trigger('change'); // Notify any JS components that the value changed
  //map.setView([e.target.feature.geometry.coordinates[1],e.target.feature.geometry.coordinates[0]], 12)
  currentStation = stationID;
  currentStationName = e.target.feature.properties.name;
  updateStn(currentStation);
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

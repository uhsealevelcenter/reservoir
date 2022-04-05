var BATTERY_PLOT_ID = "graph2";
var WATER_PLOT_ID = "graph1";
var MILLISECPERDAY = 86400000;

var time1, battery1, water_level1, time6, battery6, water_level6, maxval;

function makeplot(reservoirID, stationName, _isGMT) {
  time1 = [], battery1 = [], water_level1 = [],
  time6 = [], battery6 = [], water_level6 = [];
  // 	Plotly.d3.csv("https://uhslc.soest.hawaii.edu/reservoir/"+reservoirID+".csv", function(err, data){
  Plotly.d3.csv(URL_pre + reservoirID + v + ".csv", function(err, data) {
    if (err) {
      Plotly.purge(BATTERY_PLOT_ID);
      Plotly.purge(WATER_PLOT_ID);
      $("#graph1").text("Data for reservoir " + reservoirID + " is not available. ");
      // // alert("Water Levels data for station number: " + _stn + " is missing");
      // $("#product_desc").hide()
      console.log("ERROR");
    } else {
      $("#graph1").empty();
      $("#graph2").empty();
      // Find the selected station object from the geojson file
      var stationObject = stationPointsLayer.toGeoJSON().features.find(o => o.id === reservoirID);
      data.station = stationObject;
      processData(data, _isGMT);
      $('h1').text(stationName);


      // stationPointsLayer.eachLayer(function(layer) {
      //   console.log("NK "+layer.feature.properties.name);
      // });
    }

  });
};

function processData(allData, _isGMT) {
  // time1: scheduled transmission
  // time6: alert transmission

  // var count = 0;
  var allvals = [];
  for (var i = 0; i < allData.length; i++) {
    row = allData[i];
    if (row['data'] > -10000 && row['data'] < 99999 && row['txtype'] != 'q') 
      allvals.push(row['data']);
  }
  stdev = getSD(allvals);
  mean = getMean(allvals);
  console.log("mean: " + mean);
  console.log("stdev: " + stdev);
  var maxarr = allvals.sort(function(a,b){
     return a - b;
  });
  maxval = maxarr[maxarr.length-1]/100;
  //maxval = maxarr[maxarr.length-20]/100;
  if (maxval > (mean + 6*stdev)/100) {
     maxval = (mean + 6*stdev)/100;
  }
  console.log("maxval: " + maxval);

  var water_alerts ={
    on: allData.station.properties.level_alert_on,
    off: allData.station.properties.level_alert_off
  }

  for (var i = 0; i < allData.length; i++) {
    row = allData[i];
    //if(row['data']<-1000)
    //  row['data'] = 'NaN';
    var mydate = row['date'];
    if(_isGMT){

    }else{
      // // Use this to show in Hawaii time
      mydate = new Date(mydate);
    }

    if (row['txtype'] == 1) {

      if(_isGMT){
        time1.push(mydate);
      }else{
        // Use this to show in Hawaii time
        mydate.setHours(mydate.getHours()-10);
        mydate =  mydate.toISOString();
        time1.push(mydate);
        //////////////////////////////////
      }

      battery1.push(row['bv']);
      water_level1.push(row['data'] / 100);
      // clean out data that come at intervals longer than 5 minutes
      // by creating an artificial (mid) time point between the intervals and
      // assign it a null value
      // if (count > 0) {
      //   var date1 = new Date(time1[count]);
      //   var date2 = new Date(time1[count - 1]);
      //   var diff = date1.getTime() - date2.getTime();
      //   if (diff > 300000) {
      //     console.log(diff);
      //     time1[time1.length - 1] = (new Date((date1.getTime() + date2.getTime()) / 2));
      //     battery1[battery1.length - 1] = null;
      //     water_level1[water_level1.length - 1] = null;
      //   }
      // }
      // count += 1;
    }
    if (row['txtype'] == 6) {
      time6.push(mydate);
      battery6.push(row['bv']);
      water_level6.push(row['data'] / 100);
    }

  }


  makePlotly(time1, battery1, water_level1, time6, battery6, water_level6, _isGMT, water_alerts);
}

function makePlotly(_time1, _battery1, _water_level1, _time6, _battery6, _water_level6, _isGMT, alert) {

  var bat_scheduled = {
    x: _time1,
    y: _battery1,
    name: "Scheduled",
    type: "scatter",
    mode: "lines",
    line: {
      // color: 'rgb(0, 0, 0)',
      dash: 'solid'
    },
    marker: {
      symbol: "circle"
    },
    connectgaps: false,

  };
  var bat_alert = {
    x: _time6,
    y: _battery6,
    name: "Alert",
    type: "scatter",
    mode: "markers",
    line: {
      // color: 'rgb(255, 0, 0)',
      // dash: 'dot'
    },
    marker: {
      symbol: "circle",
      size: 10,
    },
    connectgaps: false,
  };

  var today = new Date(_time1[_time1.length - 1]);
  // Set range back to local scale and an extra hour for padding
  today.setHours(today.getHours() +11);
  // var yesterday = new Date(today.valueOf() - MILLISECPERDAY * 2);
  // var minus7days = new Date(new Date().setDate(today.getDate()-7));
  var yesterday = new Date(today.valueOf() - MILLISECPERDAY * 42);
  // console.log("today "+today);
  var title;
  if(_isGMT)
   title = "Time/Date (GMT)";
   else {
     title = "Time/Date (Pacific/Honolulu)"
   }
  var layout_bat = {
    title: "Battery Voltage",
    autosize: true,
    autoresize: true,
    xaxis: {
      //range: [minus7days, today],  // to set the xaxis range to 0 to 1
      range: [yesterday, today], // to set the xaxis range to 0 to 1
      // title: "Time/Date (" + Intl.DateTimeFormat().resolvedOptions().timeZone + ")",

      title: title,
      // autorange: true,
      rangeselector: {
        buttons: [
          {
            count: 2,
            label: '2d',
            step: 'day',
            stepmode: 'backward'
          },
          {
            count: 7,
            label: '1w',
            step: 'day',
            stepmode: 'backward'
          },
          {
            count: 42,
            label: '6w',
            step: 'day',
            stepmode: 'backward'
          }
        ],
        x: 0,
        y: 1.1
      },
      rangeslider: {},
      type: 'date'
    },
  }
  var data_bat = [bat_scheduled, bat_alert];



  var water_scheduled = {
    x: _time1,
    y: _water_level1,
    name: "Scheduled",
    type: "scatter",
    mode: "lines",
    line: {
      // color: 'rgb(0, 0, 0)',
      // dash: 'solid'
    },
    connectgaps: false,
  };
  var water_alert = {
    x: _time6,
    y: _water_level6,
    name: "Alert",
    type: "scatter",
    mode: "markers",
    line: {
      // color: 'rgb(255, 0, 0)',
      // dash: 'dot'
    },
    marker: {
      symbol: "circle",
      size: 10,
    },
    connectgaps: false,
  };

  var alert_level_on = {
    x:[_time1[0], _time1[_time1.length-1]],
    y:[alert.on, alert.on],
    name: "Alert on " + String(alert.on),
    type: "scatter",
    mode: "lines",
    line: {
      color: 'red',
      dash: 'dash'
    },
  }
  var alert_level_off = {
    x:[_time1[0], _time1[_time1.length-1]],
    y:[alert.off, alert.off],
    name: "Alert off " + String(alert.off),
    type: "scatter",
    mode: "lines",
    line: {
      color: 'green',
      dash: 'dash'
    },
  }

  var data_water = [water_scheduled, water_alert, alert_level_on, alert_level_off];
  var layout_water = {
    title: "Water level",
    autosize: true,
    autoresize: true,
    xaxis: {
      //range: [minus7days, today],  // to set the xaxis range to 0 to 1
      range: [yesterday, today], // to set the xaxis range to 0 to 1
      // title: "Time/Date (" + Intl.DateTimeFormat().resolvedOptions().timeZone + ")",
      title: title,
      // autorange: true,
      rangeselector: {
        buttons: [
          {
            count: 2,
            label: '2d',
            step: 'day',
            stepmode: 'backward'
          },
          {
            count: 7,
            label: '1w',
            step: 'day',
            stepmode: 'backward'
          },
          {
            count: 42,
            label: '6w',
            step: 'day',
            stepmode: 'backward'
          }
        ],
        x: 0,
        y: 1.1
      },
      rangeslider: {},
      type: 'date'
    },
    yaxis: {
      title: "Feet",
      //range: [(mean - 3 * stdev) / 100, (mean + 5 * stdev) / 100]
      range: [(mean - 3 * stdev) / 100, Math.max(alert.on+1, maxval+1)]
    },
  }
  var options = {
    showLink: false,
    displayLogo: false, // this one seems to not work
    modeBarButtonsToRemove: [
      // "zoom2d",
      // "pan2d",
      "select2d",
      "lasso2d",
      // "zoomIn2d",
      // "zoomOut2d",
      "autoScale2d",
      // "resetScale2d",
      "hoverClosestCartesian",
      "hoverCompareCartesian",
      "zoom3d",
      "pan3d",
      "resetCameraDefault3d",
      "resetCameraLastSave3d",
      "hoverClosest3d",
      "orbitRotation",
      "tableRotation",
      "zoomInGeo",
      "zoomOutGeo",
      // "resetGeo",
      "hoverClosestGeo",
      "toImage",
      "sendDataToCloud",
      "hoverClosestGl2d",
      "hoverClosestPie",
      "toggleHover",
      // "resetViews",
      "toggleSpikelines",
      "resetViewMapbox",
    ],
    //modeBarButtonsToAdd: ['lasso2d'],

    displayModeBar: true,
    responsive: true
  };
  console.log("battery schedule last index "+data_bat[0].x[data_bat[0].x.length-1]);
  Plotly.newPlot(BATTERY_PLOT_ID, data_bat,
    layout_bat, options);

  Plotly.newPlot(WATER_PLOT_ID, data_water,
    layout_water, options);
};


//
// function updateTime(isLocal) {
//   // console.log("TIMEZONE "+tz);
//   var xLabel;
//   var tv1 = {
//     x: []
//   };
//   var tv6 = {
//     x: []
//   };
//
//   if (isLocal) {
//     xLabel = "Time/Date (" + Intl.DateTimeFormat().resolvedOptions().timeZone + ")";
//     time1.forEach(element => tv1.x.push(convertTime(element));
//     time6.forEach(element => tv6.x.push(element));
//   } else {
//     xLabel = "Time/Date (GMT)";
//     time1.forEach(element => tv1.x.push((element)));
//     time6.forEach(element => tv6.x.push(convertTime(element)));
//   }
//   console.log("xLabel " + xLabel);
//
//   var bat_scheduled = {
//     x: tv1.x,
//   };
//   var bat_alert = {
//     x: tv6.x,
//   };
//
//   // var date = new Date(row[key]);
//   // date.setHours(date.getHours() + lst);
//   // return date.toISOString();
//
//   var data_bat = [bat_scheduled, bat_alert];
//
//   console.log("battery schedule last index "+data_bat[0].x[data_bat[0].x.length-1]);
//   var today = new Date(tv1.x[tv1.x.length - 1]);
//   var yesterday = new Date(today.valueOf() - MILLISECPERDAY * 2);
//
//   var layout_update = {
//     xaxis: {
//       //range: [minus7days, today],  // to set the xaxis range to 0 to 1
//       range: [yesterday, today], // to set the xaxis range to 0 to 1
//       title: xLabel,
//       // autorange: true,
//       rangeselector: {
//         buttons: [{
//             count: 2,
//             label: '2d',
//             step: 'day',
//             stepmode: 'backward'
//           },
//           {
//             count: 7,
//             label: '1w',
//             step: 'day',
//             stepmode: 'backward'
//           },
//           {
//             count: 42,
//             label: '6w',
//             step: 'day',
//             stepmode: 'backward'
//           }
//         ],
//         x: 0,
//         y: 1.1
//       },
//       rangeslider: {},
//       type: 'date'
//     },
//   }
//
//   // Plotly.update(WATER_PLOT_ID, data_update, layout_update);
//   Plotly.update(BATTERY_PLOT_ID, data_bat, layout_update);
// }

// function convertTime(dateString){
//   var date = new Date(dateString);
//   date.setHours(date.getHours() -10);
//   return date.toISOString();
// }

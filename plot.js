function makeplot(reservoirID, stationName) {
// 	Plotly.d3.csv("https://uhslc.soest.hawaii.edu/reservoir/"+reservoirID+".csv", function(err, data){
 	Plotly.d3.csv(URL_pre + reservoirID + ".csv", function(err, data){
    if (err) {
          Plotly.purge("graph1");
          Plotly.purge("graph2");
          $("#graph1").text("Data for reservoir " + reservoirID + " is not available. ");
          // // alert("Water Levels data for station number: " + _stn + " is missing");
          // $("#product_desc").hide()
          console.log("ERROR");
        } else {
          $("#graph1").empty();
          processData(data);
          $('h1').text(stationName);
        }

  } );

};

function processData(allRows) {
  // time1: scheduled transmission
  // time6: alert transmission
	var time1 = [], battery1 = [], water_level1 = [];
  var time6 = [], battery6 = [], water_level6 = [];
  var count = 0;
  var allvals = [];
  for (var i=0; i<allRows.length; i++) {
      row = allRows[i];
      allvals.push(row['data']);
  }
  var outlier = getOutlier(allvals);
  console.log(outlier);
  for (var i=0; i<allRows.length; i++) {
    row = allRows[i];
    //if(row['data']<-1000)
    //  row['data'] = 'NaN';
    if (row['data'] < -4*outlier || row['data'] > 4*outlier)
      row['data'] = 'NaN';
    if (row['txtype'] == 1)
		  {
        time1.push( new Date(row['date']) );
		    battery1.push( row['bv'] );
        water_level1.push(row['data']/100);
        // clean out data that come at intervals longer than 5 minutes
        // by creatiing an artificial (mid) time point between the intervals and
        // assign it a null value
        if(count>0){
          var date1 = new Date(time1[count]);
          var date2 = new Date(time1[count-1]);
          var diff = date1.getTime() - date2.getTime();
          if(diff>300000)
            {
              // console.log(diff);
              time1[time1.length-1]=(new Date((date1.getTime() + date2.getTime())/2));
              battery1[battery1.length-1]=null;
              water_level1[water_level1.length-1]=null;
            }
        }
        count += 1;
      }
    if (row['txtype'] == 6)
		  {
        time6.push( new Date(row['date']) );
		    battery6.push( row['bv'] );
        water_level6.push(row['data']/100);
      }

	}


	makePlotly( time1, battery1, water_level1, time6, battery6, water_level6 );
}

function makePlotly( time, battery1, water_level1 , time6, battery6, water_level6){
	var plotDiv = document.getElementById("plot");
	var bat_scheduled = {
		x: time,
		y: battery1,
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
		x: time6,
		y: battery6,
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
  var MILLISECPERDAY = 86400000;
  var today = new Date(time[time.length-1]);
  var yesterday = new Date(today.valueOf() - MILLISECPERDAY*2);
  // var minus7days = new Date(new Date().setDate(today.getDate()-7));
  // console.log("minus7days "+minus7days);
  var layout_bat = {
    title: "Battery Voltage",
    autoresize: true,
    xaxis: {
   //range: [minus7days, today],  // to set the xaxis range to 0 to 1
   range: [yesterday, today],  // to set the xaxis range to 0 to 1
   title: "Time/Date ("+Intl.DateTimeFormat().resolvedOptions().timeZone+")",
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
		x: time,
		y: water_level1,
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
		x: time6,
		y: water_level6,
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
  var data_water = [water_scheduled, water_alert];
  var layout_water = {
    title: "Water level",
    xaxis: {
   //range: [minus7days, today],  // to set the xaxis range to 0 to 1
   range: [yesterday, today],  // to set the xaxis range to 0 to 1
   title: "Time/Date ("+Intl.DateTimeFormat().resolvedOptions().timeZone+")",
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
  };
	Plotly.newPlot('graph1', data_bat,
		layout_bat, options);

    Plotly.newPlot('graph2', data_water,
  		layout_water, options);
};

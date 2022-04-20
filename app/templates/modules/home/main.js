

var socket = io();

var objHsvData = {
    "hue": {
        "max": 0,
        "min": 0
    },
    "saturation": {
        "max": 0,
        "min": 0
    },
    "value": {
        "max": 0,
        "min": 0
    }
}

var imageProcesData = {
    "subtractTreshVal": parseInt(subtractTreshVal.value),
}

socket.on('home-connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});

});

// global treshold parameters
socket.on('data-params', function (data) {
    var data = JSON.parse(data)
    document.getElementById("subtractTreshVal").value = data.subtractTreshVal
    document.getElementById("subtractTreshValText").value = data.subtractTreshVal
});

socket.on('hsv-obj-data', function (data) {
    var JSON_received = JSON.parse(data);
    // chart_histObj.update(JSON_received);
});

// ----------------------------------------------------------------------------------------- //
// reconstruction data
// 
//  data = {
//      "ptCloud" : {
//          "x"
//          "y"
//          "z"
//      },
//  "volume"
//  "length"
//  "computeTime"
//  }
// 
socket.on('reconstruction-data', function (data) {
    var JSON_received = JSON.parse(data);
    // ptChart.update(JSON_received);

    document.getElementById("totalPointCloud").innerHTML = JSON_received.ptCloud.x.length + JSON_received.ptCloud.y.length + JSON_received.ptCloud.z.length;
    document.getElementById("computeTime").innerHTML = JSON_received.computeTime.toFixed(3);
    document.getElementById("volume").innerHTML = JSON_received.volume.toFixed(2);
    document.getElementById("length").innerHTML = JSON_received.length.toFixed(2);
    // Set explicit Y Axis interval.
    // chart3D.getDefaultAxisY().setInterval(0, 150, 2000, true)
});


document.addEventListener('DOMContentLoaded', (event) => {
    hsvChart_create('histObjH', 'histObjS', 'histObjV');
    uiSlide_create();
    socket.emit('get-data', {message: 'get-imagep-process-data'});
    socket.emit('get-config', {message: 'get-config'});
})



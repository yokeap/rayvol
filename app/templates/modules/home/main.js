

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
socket.on('data-home-params', function (data) {
    var data = JSON.parse(data)
    document.getElementById("subtractTreshVal").value = data.subtractTreshVal
    document.getElementById("subtractTreshValText").value = data.subtractTreshVal
});

socket.on('hsv-obj-data', function (data) {
    var JSON_received = JSON.parse(data);
    // hsvChart_update(JSON_received);
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
    // console.log(JSON_received)
    document.getElementById("data-totalpointcloud").innerHTML = JSON_received.ptCloud.x.length + JSON_received.ptCloud.y.length + JSON_received.ptCloud.z.length;
    document.getElementById("data-reconsructiontime").innerHTML = JSON_received.computeTime.toFixed(3);
    document.getElementById("data-volume").innerHTML = JSON_received.volume.toFixed(2);
    document.getElementById("data-length").innerHTML = JSON_received.length.toFixed(2);
    document.getElementById("data-width").innerHTML = JSON_received.width.toFixed(2);
    document.getElementById("data-height").innerHTML = JSON_received.height.toFixed(2);
    // Set explicit Y Axis interval.
    // chart3D.getDefaultAxisY().setInterval(0, 150, 2000, true)
});


document.addEventListener('DOMContentLoaded', (event) => {
    hsvChart_create('histObjH', 'histObjS', 'histObjV');
    // uiSlide_create();
    socket.emit('home-connect', {message: 'home page has been connected'});  
    socket.emit('get-data', {message: 'process-data'});
    // socket.emit('get-data', {message: 'get-config'});
})

// setInterval(function() {
//     var obj_feed = document.getElementById("obj_feed");
//     obj_feed.src = "/image_obj_feed";
//     console.log(obj_feed);
// }, 1000);


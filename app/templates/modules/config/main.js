// config.html script //

var socket = io();

var exposure = document.getElementById("expVal"),
    brightness = document.getElementById("brightnessVal"),
    contrast = document.getElementById("contrastVal"),
    hue = document.getElementById("hueVal"),
    saturation = document.getElementById("saturationVal"),
    sharpness = document.getElementById("sharpnessVal");

var exposureText = document.getElementById("expValText"),
    brightnessText = document.getElementById("brightnessValText"),
    contrastText = document.getElementById("contrastValText"),
    hueText = document.getElementById("hueValText"),
    saturationText = document.getElementById("saturationValText"),
    sharpnessText = document.getElementById("sharpnessValText"); 

socket.on('data-config-params', function (data) {
    var data = JSON.parse(data)
    configs = data;
    // console.log(configs);
    document.getElementById("expVal").value = data.exposure;
    document.getElementById("brightnessVal").value = data.brightness;
    document.getElementById("contrastVal").value = data.contrast;
    document.getElementById("hueVal").value = data.hue;
    document.getElementById("saturationVal").value = data.saturation;
    document.getElementById("sharpnessVal").value = data.sharpness;

    document.getElementById("expValText").value = data.exposure;
    document.getElementById("brightnessValText").value = data.brightness;
    document.getElementById("contrastValText").value = data.contrast;
    document.getElementById("hueValText").value = data.hue;
    document.getElementById("saturationValText").value = data.saturation;
    document.getElementById("sharpnessValText").value = data.sharpness;
});

socket.on('hsv-config-data', function (data) {
    var JSON_received = JSON.parse(data);
    hsvChart_update(JSON_received);
});


document.addEventListener('DOMContentLoaded', (event) => {
    socket.emit('config-connect', {message: 'config page has been connected'});  
    hsvChart_create('histObjH', 'histObjS', 'histObjV');
    // uiSlide_create();
    // socket.emit('get-data', {message: 'get-imagep-process-data'});
    // socket.emit('get-config', {message: 'get-config'});
})


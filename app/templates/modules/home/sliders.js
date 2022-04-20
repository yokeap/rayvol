var sliderObjH = document.getElementById('slider-h-obj')
    , sliderObjS = document.getElementById('slider-s-obj')
    , sliderObjV = document.getElementById('slider-v-obj');


const sliderConfig = {
    start: [0.2, 0.8],
    connect: true,
    range: {
        'min': 0,
        'max': 1
    }
}

function uiSlide_create() {
    noUiSlider.create(sliderObjH, sliderConfig);
    noUiSlider.create(sliderObjS, sliderConfig);
    noUiSlider.create(sliderObjV, sliderConfig);
}

document.querySelectorAll('[type=slider_hsv]').forEach(
    slider_hsv => slider_hsv.noUiSlider.on('update', function(data) {
        switch (slider_hsv.id) {
            case "slider-h-obj": 
                objHsvData.hue.min = data[0];
                objHsvData.hue.max = data[1];
                socket.emit('slider-obj-hsv', JSON.stringify(objHsvData));
                break;
            case "slider-s-obj": 
                objHsvData.saturation.min = data[0];
                objHsvData.saturation.max = data[1];
                socket.emit('slider-obj-hsv', JSON.stringify(objHsvData));
                break;
            case "slider-v-obj": 
                objHsvData.value.min = data[0];
                objHsvData.value.max = data[1];
                socket.emit('slider-obj-hsv', JSON.stringify(objHsvData));
                break;
        }

    })
);

// bootstrap ranage update event
var ranges = document.querySelectorAll('input[type=range]');
ranges.forEach(
    range => range.addEventListener('input', () => {
            // console.log(range.id);
            if(range.id === "subtractTreshVal"){
                subtractTreshValText.value = range.value;
                imageProcesData.subtractTreshVal = parseInt(range.value);
                socket.emit('process-value', JSON.stringify(imageProcesData))
            }
        }
    )
);
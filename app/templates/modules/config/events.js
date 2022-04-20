var configs = {
    exposure : 0,
    brightness : 0,
    contrast : 0,
    hue : 0,
    saturation : 0,
    sharpness : 0,
};

function saveBackground(){
    socket.emit('capture-background', JSON.stringify({ capture : true }))
    var messageModal = new bootstrap.Modal(document.getElementById('messageModal'), {});
    document.getElementById("modal-text").innerHTML = "Background is captured";
    messageModal.toggle()
}

function saveParams(){
    socket.emit('save-config', JSON.stringify({ saveConfigs : true }))
    var messageModal = new bootstrap.Modal(document.getElementById('messageModal'), {});
    document.getElementById("modal-text").innerHTML = "Configs have been saved";
    messageModal.toggle();
}

var ranges = document.querySelectorAll('input[type=range]');
ranges.forEach(
    range => range.addEventListener('input', () => {
            // console.log(range.id);
            if(range.id === "expVal"){
                exposureText.value = range.value;
                configs.expVal = parseInt(range.value);
            }
            if(range.id === "brightnessVal"){
                brightnessText.value = range.value;
                configs.brightnessVal = parseInt(range.value);
            }
            if(range.id === "contrastVal"){
                contrastText.value = range.value;
                configs.contrastVal = parseInt(range.value);
            }
            if(range.id === "hueVal"){
                hueText.value = range.value;
                configs.hueVal = parseInt(range.value);
            }
            if(range.id === "saturationVal"){
                saturationText.value = range.value;
                configs.saturationVal = parseInt(range.value);
            }
            if(range.id === "sharpnessVal"){
                sharpnessText.value = range.value;
                configs.sharpnessVal = parseInt(range.value);
            }
            socket.emit('config-value', JSON.stringify(configs))
        }
    )
);

var texts = document.querySelectorAll('input[type=text]');
texts.forEach(
    text => text.addEventListener('keypress', (e) => {
            // console.log(text.id);
            if(e.key == 'Enter') {
                if(text.id === "expValText"){
                    exposure.value = text.value;
                    configs.expVal = parseInt(text.value);
                }
                if(text.id === "brightnessValText"){
                    brightness.value = text.value;
                    configs.brightnessVal = parseInt(text.value);
                }
                if(text.id === "contrastValText"){
                    contrast.value = text.value;
                    configs.contrastVal = parseInt(text.value);
                }
                if(text.id === "hueValText"){
                    hue.value = text.value;
                    configs.hueVal = parseInt(text.value);
                }
                if(text.id === "saturationValText"){
                    saturation.value = text.value;
                    configs.saturationVal = parseInt(text.value);
                }
                if(text.id === "sharpnessValText"){
                    sharpness.value = text.value;
                    configs.sharpnessVal = parseInt(text.value);
                }
                socket.emit('config-value', JSON.stringify(configs))
            }
        }
    )
);
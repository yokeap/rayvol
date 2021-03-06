function saveCapture(){
    json= {
        capture: true,
        sample_number: document.getElementById("sname").value 
    }
    socket.emit('capture', JSON.stringify(json))
    var messageModal = new bootstrap.Modal(document.getElementById('messageModal'), {});
    document.getElementById("modal-text").innerHTML = "Data and picture have been saved";
    messageModal.toggle()
}

function saveParams(){
    socket.emit('save-params', JSON.stringify({ saveParams : true }))
    var messageModal = new bootstrap.Modal(document.getElementById('messageModal'), {});
    document.getElementById("modal-text").innerHTML = "Parameters have been saved";
    messageModal.toggle();
}

var ranges = document.querySelectorAll('input[type=range]');
ranges.forEach(
    range => range.addEventListener('input', () => {
            // console.log(range.id);
            if(range.id === "subtractTreshVal"){
                subtractTreshValText.value = range.value;
                objProcessData.subtractTreshVal = parseInt(range.value);
                socket.emit('process-value', JSON.stringify(objProcessData))
            }
        }
    )
);

var radios = document.querySelectorAll('input[type=radio]');
radios.forEach(
    radio => radio.addEventListener('change', () => {
            socket.emit('feed-status', JSON.stringify({ feedStatus : radio.value }))
        }
    )
);

var checkboxs = document.querySelectorAll('input[type=checkbox]');
checkboxs.forEach(
    checkbox => checkbox.addEventListener('change', () => {
        console.log(checkbox);
            // change view raw stream or 3D reconstruction view
            if(checkbox.id == "swt3d"){
                if(checkbox.checked == true){
                    document.getElementById("streamRaw").style.display = "none";
                    // document.getElementById("3dChart").style.display = "inline";
                }
                else {
                    document.getElementById("streamRaw").style.display = "inline";
                    // document.getElementById("3dChart").style.display = "none";
                }
            }
        }
    )
);
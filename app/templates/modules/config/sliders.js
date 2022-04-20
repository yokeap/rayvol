

// // bootstrap ranage update event
// var ranges = document.querySelectorAll('input[type=range]');
// ranges.forEach(
//     range => range.addEventListener('input', () => {
//             // console.log(range.id);
//             if(range.id === "subtractTreshVal"){
//                 subtractTreshValText.value = range.value;
//                 imageProcesData.subtractTreshVal = parseInt(range.value);
//                 socket.emit('process-value', JSON.stringify(imageProcesData))
//             }
//         }
//     )
// );
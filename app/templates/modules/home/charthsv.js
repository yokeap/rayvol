'use strict'

var chartHConfig = {
    responsive: false,
    maintainAspectRatio: true,
    type: "line",
    data: {
        labels: hsvChart_360num(),
        datasets: [{
            backgroundColor: [
                'rgba(153, 102, 255, 1)',
            ],
            borderColor: [
                'rgba(153, 102, 255, 1)',
            ],
            data: [],
            fill: false,
            borderWidth: 1,
            pointRadius: 0,
        }]
    },
    options: {
        plugins: {
            filler: {
                propagate: false,
            },
            title: {
                display: true,
                text: "Hue",
                color: 'white'
            },
            legend: {
                display: false,
            },
            layout: {
                padding: 0
            }
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                },
                beginAtZero: true
            },
            x: {
                type: 'linear',
                min: 0,
                max: 360,
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                    stepSize: 50,
                },
                beginAtZero: true
            }
        }

    }
}

var chartSConfig = {
    responsive: false,
    maintainAspectRatio: false,
    type: "line",
    data: {
        labels: hsvChart_256num(),
        datasets: [{
            backgroundColor: [
                'rgba(153, 102, 255, 0.2)',
            ],
            borderColor: [
                'rgba(153, 102, 255, 1)',
            ],
            data: [],
            fill: false,
            borderWidth: 1,
            pointRadius: 0,
        }]
    },
    options: {
        plugins: {
            filler: {
                propagate: false,
            },
            title: {
                display: true,
                text: "Saturation",
                color: 'white'
            },
            legend: {
                display: false,
            }
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                },
                beginAtZero: true
            },
            x: {
                type: 'linear',
                min: 0,
                max: 255,
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                    stepSize: 50,
                },
                beginAtZero: true
            }
        }

    }
}

var chartVConfig = {
    responsive: false,
    maintainAspectRatio: false,
    type: "line",
    data: {
        labels: hsvChart_256num(),
        datasets: [{
            backgroundColor: [
                'rgba(153, 102, 255, 0.2)',
            ],
            borderColor: [
                'rgba(153, 102, 255, 1)',
            ],
            data: [],
            fill: false,
            borderWidth: 1,
            pointRadius: 0,
        }]
    },
    options: {
        plugins: {
            filler: {
                propagate: false,
            },
            title: {
                display: true,
                text: "Value",
                color: 'white'
            },
            legend: {
                display: false,
            }
        },
        scales: {
            y: {
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                },
                beginAtZero: true
            },
            x: {
                type: 'linear',
                min: 0,
                max: 255,
                grid: {
                    color: 'rgba(255, 159, 64, 0.1)',
                    drawTicks: false,
                },
                ticks: {
                    color: 'rgba(255, 159, 64, 1)',
                    stepSize: 50,
                },
                beginAtZero: true
            }
        }

    }
}


var chart_histObjH, chart_histObjS, chart_histObjV;

function hsvChart_create(id_h, id_s, id_v) {
    if (chart_histObjH instanceof Chart) {
        chart_histObjH.destroy();
    }

    if (chart_histObjS instanceof Chart) {
        chart_histObjS.destroy();
    }

    if (chart_histObjV instanceof Chart) {
        chart_histObjV.destroy();
    }

    chart_histObjH = new Chart(document.getElementById(id_h), chartHConfig);
    chart_histObjS = new Chart(document.getElementById(id_s), chartSConfig);
    chart_histObjV = new Chart(document.getElementById(id_v), chartVConfig);
}

function hsvChart_update(data) {
    if (chart_histObjH instanceof Chart) {
        chart_histObjH.options.scales.y.max = JSON_received.hist_h_ymax;
        chart_histObjH.data.datasets[0].data = data.hist_h[0];
        chart_histObjH.update();
    }
    if (chart_histObjS instanceof Chart) {
        chart_histObjS.options.scales.y.max = JSON_received.hist_s_ymax;
        chart_histObjS.data.datasets[0].data = data.hist_s[0];
        chart_histObjS.update();
    }
    if (chart_histObjV instanceof Chart) {
        chart_histObjV.options.scales.y.max = JSON_received.hist_v_ymax;
        chart_histObjV.data.datasets[0].data = data.hist_v[0];
        chart_histObjV.update();
    }
}

function hsvChart_generateData(hist) {
    var xValues = [];
    var yValues = [];
    for (let i = 0; i < hist.shape[0]; i++) {
        xValues.push(i);
        yValues.push(hist[0])
    }
}

function hsvChart_256num() {
    var xValues = [];
    for (let i = 0; i < 256; i++) {
        xValues.push(i);
    }
    return xValues;
}

function hsvChart_360num() {
    var xValues = [];
    for (let i = 0; i < 360; i++) {
        xValues.push(i);
    }
    return xValues;
}
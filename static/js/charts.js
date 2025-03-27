/**
 * Charts.js for Lead Management System
 * Functions for creating and updating charts used throughout the application
 */

/**
 * Creates a line chart with the given data
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for X axis
 * @param {array} data - Data points
 * @param {string} color - Main color (defaults to purple)
 */
function createLineChart(canvasId, title, labels, data, color = 'rgba(128, 90, 213, 1)') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const lightColor = color.replace('1)', '0.2)');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: lightColor,
                borderColor: color,
                borderWidth: 2,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: color,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: color,
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates a bar chart with the given data
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for X axis
 * @param {array} data - Data points
 * @param {string} color - Main color (defaults to purple)
 */
function createBarChart(canvasId, title, labels, data, color = 'rgba(128, 90, 213, 1)') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const lightColor = color.replace('1)', '0.7)');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: lightColor,
                borderColor: color,
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: color,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: color,
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates a pie chart with the given data
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for sections
 * @param {array} data - Data points
 */
function createPieChart(canvasId, title, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const backgroundColors = [
        'rgba(128, 90, 213, 0.8)',   // Purple (Primary)
        'rgba(75, 192, 192, 0.8)',    // Teal
        'rgba(255, 159, 64, 0.8)',    // Orange
        'rgba(54, 162, 235, 0.8)',    // Blue
        'rgba(255, 99, 132, 0.8)',    // Red
        'rgba(255, 205, 86, 0.8)',    // Yellow
        'rgba(153, 102, 255, 0.8)'    // Purple (Alternative)
    ];
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(25, 25, 25, 1)',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates a doughnut chart with the given data
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for sections
 * @param {array} data - Data points
 */
function createDoughnutChart(canvasId, title, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const backgroundColors = [
        'rgba(128, 90, 213, 0.8)',   // Purple (Primary)
        'rgba(75, 192, 192, 0.8)',    // Teal
        'rgba(255, 159, 64, 0.8)',    // Orange
        'rgba(54, 162, 235, 0.8)',    // Blue
        'rgba(255, 99, 132, 0.8)',    // Red
        'rgba(255, 205, 86, 0.8)',    // Yellow
        'rgba(153, 102, 255, 0.8)'    // Purple (Alternative)
    ];
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(25, 25, 25, 1)',
                borderWidth: 2,
                hoverOffset: 10,
                cutout: '60%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates a stacked bar chart for comparing multiple data sets
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for X axis
 * @param {array} datasets - Array of dataset objects
 */
function createStackedBarChart(canvasId, title, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    color: 'rgba(255, 255, 255, 0.9)',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    stacked: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates an area chart for showing trends over time
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for X axis
 * @param {array} data - Data points
 * @param {string} color - Main color (defaults to purple)
 */
function createAreaChart(canvasId, title, labels, data, color = 'rgba(128, 90, 213, 1)') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const lightColor = color.replace('1)', '0.2)');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: lightColor,
                borderColor: color,
                borderWidth: 2,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: color,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.4,
                fill: 'origin'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: color,
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Creates a polar area chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for sections
 * @param {array} data - Data points
 */
function createPolarAreaChart(canvasId, title, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const backgroundColors = [
        'rgba(128, 90, 213, 0.7)',   // Purple (Primary)
        'rgba(75, 192, 192, 0.7)',    // Teal
        'rgba(255, 159, 64, 0.7)',    // Orange
        'rgba(54, 162, 235, 0.7)',    // Blue
        'rgba(255, 99, 132, 0.7)',    // Red
        'rgba(255, 205, 86, 0.7)',    // Yellow
        'rgba(153, 102, 255, 0.7)'    // Purple (Alternative)
    ];
    
    return new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(25, 25, 25, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    displayColors: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        backdropColor: 'rgba(0, 0, 0, 0.4)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Updates an existing chart with new data
 * @param {object} chart - The Chart.js chart object
 * @param {array} labels - New labels
 * @param {array} data - New data points
 */
function updateChart(chart, labels, data) {
    if (!chart) return;
    
    chart.data.labels = labels;
    
    if (Array.isArray(data)) {
        // For single dataset charts
        chart.data.datasets[0].data = data;
    } else if (typeof data === 'object') {
        // For multi-dataset charts
        Object.keys(data).forEach((key, index) => {
            if (chart.data.datasets[index]) {
                chart.data.datasets[index].data = data[key];
            }
        });
    }
    
    chart.update();
}

/**
 * Creates a multi-line chart for comparing multiple data sets
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {array} labels - Labels for X axis
 * @param {array} datasets - Array of dataset objects
 */
function createMultiLineChart(canvasId, title, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map((dataset, index) => {
                // Predefined colors for consistency
                const colors = [
                    'rgba(128, 90, 213, 1)',   // Purple (Primary)
                    'rgba(75, 192, 192, 1)',   // Teal
                    'rgba(255, 159, 64, 1)',   // Orange
                    'rgba(54, 162, 235, 1)',   // Blue
                    'rgba(255, 99, 132, 1)',   // Red
                    'rgba(255, 205, 86, 1)'    // Yellow
                ];
                
                const color = colors[index % colors.length];
                const lightColor = color.replace('1)', '0.2)');
                
                return {
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: lightColor,
                    borderColor: color,
                    borderWidth: 2,
                    pointBackgroundColor: color,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: color,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.4,
                    fill: false
                };
            })
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: title,
                    color: 'rgba(255, 255, 255, 0.9)',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Helper function to generate gradient for charts
 * @param {object} ctx - Canvas context
 * @param {string} startColor - Start color in rgba format
 * @param {string} endColor - End color in rgba format
 * @returns {object} - Canvas gradient object
 */
function createGradient(ctx, startColor, endColor) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
}

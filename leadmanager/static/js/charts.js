/**
 * Charts and data visualization for Lead Management System
 */

// Load Chart.js from CDN if not already loaded
function loadChartJS() {
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js';
        script.onload = loadCharts;
        document.head.appendChild(script);
    } else {
        loadCharts();
    }
}

// Load all charts on the page
function loadCharts() {
    // Set default chart colors based on theme
    Chart.defaults.color = '#FFFFFF';
    Chart.defaults.borderColor = '#3D3D3D';
    
    // Create charts for elements with data-chart attribute
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart');
        const chartId = element.getAttribute('id');
        
        switch(chartType) {
            case 'leads-status':
                createLeadsStatusChart(chartId);
                break;
            case 'leads-source':
                createLeadsSourceChart(chartId);
                break;
            case 'sales-performance':
                createSalesPerformanceChart(chartId);
                break;
            case 'project-status':
                createProjectStatusChart(chartId);
                break;
            case 'payment-trends':
                createPaymentTrendsChart(chartId);
                break;
            case 'task-distribution':
                createTaskDistributionChart(chartId);
                break;
            case 'employee-hours':
                createEmployeeHoursChart(chartId);
                break;
            case 'monthly-leads':
                createMonthlyLeadsChart(chartId);
                break;
            case 'revenue-target':
                createRevenueTargetChart(chartId);
                break;
        }
    });
}

// Create leads status distribution chart
function createLeadsStatusChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#7C4DFF',  // Purple
                    '#2196F3',  // Blue
                    '#00C853',  // Green
                    '#FFD600',  // Yellow
                    '#F44336',  // Red
                    '#FF9800',  // Orange
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FFFFFF',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1,
                    displayColors: true,
                    usePointStyle: true,
                }
            },
            cutout: '65%',
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create leads source distribution chart
function createLeadsSourceChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads Count',
                data: data,
                backgroundColor: '#7C4DFF',
                borderColor: '#6200EA',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            },
            barPercentage: 0.6
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create sales performance chart
function createSalesPerformanceChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads Converted',
                data: data,
                backgroundColor: '#7C4DFF',
                borderColor: '#6200EA',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            },
            barPercentage: 0.7
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create project status chart
function createProjectStatusChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#2196F3',  // Blue
                    '#FFD600',  // Yellow
                    '#00C853',  // Green
                    '#F44336',  // Red
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FFFFFF',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create payment trends chart
function createPaymentTrendsChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Payment Amount',
                data: data,
                backgroundColor: 'rgba(124, 77, 255, 0.2)',
                borderColor: '#7C4DFF',
                borderWidth: 2,
                pointBackgroundColor: '#6200EA',
                pointBorderColor: '#FFFFFF',
                pointRadius: 4,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return '$' + context.raw;
                        }
                    }
                }
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create task distribution chart
function createTaskDistributionChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(33, 150, 243, 0.7)',  // Blue
                    'rgba(255, 214, 0, 0.7)',   // Yellow
                    'rgba(0, 200, 83, 0.7)',    // Green
                    'rgba(244, 67, 54, 0.7)',   // Red
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FFFFFF',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            },
            scales: {
                r: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: '#FFFFFF'
                    }
                }
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create employee hours chart
function createEmployeeHoursChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const dataString = element.getAttribute('data-values');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const data = JSON.parse(dataString || '[]');
    
    // Chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hours Worked',
                data: data,
                backgroundColor: '#7C4DFF',
                borderColor: '#6200EA',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            },
            barPercentage: 0.6
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create monthly leads chart
function createMonthlyLeadsChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const labelString = element.getAttribute('data-labels');
    const newLeadsString = element.getAttribute('data-new-leads');
    const convertedLeadsString = element.getAttribute('data-converted-leads');
    
    // Parse JSON data
    const labels = JSON.parse(labelString || '[]');
    const newLeads = JSON.parse(newLeadsString || '[]');
    const convertedLeads = JSON.parse(convertedLeadsString || '[]');
    
    // Chart configuration
    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'New Leads',
                    data: newLeads,
                    backgroundColor: 'rgba(33, 150, 243, 0.2)',
                    borderColor: '#2196F3',
                    borderWidth: 2,
                    pointBackgroundColor: '#1E88E5',
                    pointBorderColor: '#FFFFFF',
                    pointRadius: 4,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Converted Leads',
                    data: convertedLeads,
                    backgroundColor: 'rgba(0, 200, 83, 0.2)',
                    borderColor: '#00C853',
                    borderWidth: 2,
                    pointBackgroundColor: '#00B248',
                    pointBorderColor: '#FFFFFF',
                    pointRadius: 4,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#FFFFFF',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1F1F1F',
                    titleColor: '#FFFFFF',
                    bodyColor: '#BDBDBD',
                    borderColor: '#3D3D3D',
                    borderWidth: 1
                }
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
}

// Create revenue target chart
function createRevenueTargetChart(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Get data from data attributes
    const currentValue = parseFloat(element.getAttribute('data-current') || 0);
    const targetValue = parseFloat(element.getAttribute('data-target') || 100);
    
    // Calculate percentage
    const percentage = Math.min(Math.round((currentValue / targetValue) * 100), 100);
    
    // Chart configuration
    const config = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percentage, 100 - percentage],
                backgroundColor: [
                    '#7C4DFF',  // Purple
                    '#2C2C2C',  // Dark Grey
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            rotation: -90,
            circumference: 180,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            animation: {
                animateRotate: true
            }
        }
    };
    
    // Create chart
    new Chart(element, config);
    
    // Add centered text
    const centerText = document.createElement('div');
    centerText.style.position = 'absolute';
    centerText.style.top = '50%';
    centerText.style.left = '50%';
    centerText.style.transform = 'translate(-50%, -65%)';
    centerText.style.textAlign = 'center';
    
    const percentageText = document.createElement('div');
    percentageText.style.fontSize = '28px';
    percentageText.style.fontWeight = '700';
    percentageText.style.color = '#FFFFFF';
    percentageText.textContent = `${percentage}%`;
    
    const labelText = document.createElement('div');
    labelText.style.fontSize = '14px';
    labelText.style.color = '#BDBDBD';
    labelText.textContent = 'of target';
    
    centerText.appendChild(percentageText);
    centerText.appendChild(labelText);
    
    // Position the element wrapper relatively for absolute positioning of text
    element.parentElement.style.position = 'relative';
    element.parentElement.appendChild(centerText);
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', loadChartJS);

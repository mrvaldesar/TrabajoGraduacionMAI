import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('pieChart') pieCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('barChart') barCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('lineChart') lineCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('latencyChart') latencyCanvas!: ElementRef<HTMLCanvasElement>;

  private pieChart: Chart | undefined;
  private barChart: Chart | undefined;
  private lineChart: Chart | undefined;
  private latencyChart: Chart | undefined;

  totalOperations = 0;
  lastUpdate: Date = new Date();

  // New KPIs
  avgClassifyTime = 0;
  avgSimilarityTime = 0;

  constructor() {
    Chart.register(...registerables);
  }

  ngOnInit(): void {
    // Basic init
  }

  ngAfterViewInit(): void {
    this.renderCharts();
  }

  ngOnDestroy(): void {
    this.pieChart?.destroy();
    this.barChart?.destroy();
    this.lineChart?.destroy();
    this.latencyChart?.destroy();
  }

  renderCharts() {
    const rawHistory = localStorage.getItem('nlp_history');
    const history: any[] = rawHistory ? JSON.parse(rawHistory) : [];

    this.totalOperations = history.length;
    this.lastUpdate = new Date();

    // --- KPI CALCULATIONS ---
    const classifyItems = history.filter(h => h.type === 'Clasificación' && h.metrics && h.metrics.inference_time);
    const similarityItems = history.filter(h => h.type === 'Similitud' && h.metrics && h.metrics.inference_time);

    if (classifyItems.length > 0) {
      const totalTime = classifyItems.reduce((acc, curr) => acc + curr.metrics.inference_time, 0);
      this.avgClassifyTime = totalTime / classifyItems.length;
    } else {
      this.avgClassifyTime = 0;
    }

    if (similarityItems.length > 0) {
      const totalTime = similarityItems.reduce((acc, curr) => acc + curr.metrics.inference_time, 0);
      this.avgSimilarityTime = totalTime / similarityItems.length;
    } else {
      this.avgSimilarityTime = 0;
    }

    // 1. Process Classification Data (Pie Chart)
    const categoryCounts: { [key: string]: number } = {};
    history.filter(h => h.type === 'Clasificación').forEach(h => {
        const cat = h.result || 'Desconocido';
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
    });

    const pieLabels = Object.keys(categoryCounts);
    const pieData = Object.values(categoryCounts);

    // 2. Process Similarity Data (Bar Chart - Histogram)
    // Buckets: 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0
    const buckets = [0, 0, 0, 0, 0];
    const bucketLabels = ['0.0 - 0.2', '0.2 - 0.4', '0.4 - 0.6', '0.6 - 0.8', '0.8 - 1.0'];

    history.filter(h => h.type === 'Similitud').forEach(h => {
        // Expected format: "Score: 0.1234"
        const match = (h.result || '').match(/Score:\s*([\d.]+)/);
        if (match && match[1]) {
            const score = parseFloat(match[1]);
            if (score >= 0 && score <= 1) {
                const index = Math.min(Math.floor(score / 0.2), 4);
                buckets[index]++;
            }
        }
    });

    // 3. Process Activity Data (Line Chart - Last 7 Days)
    const activityMap: { [key: string]: number } = {};
    // 4. Process Latency Evolution Data (Line Chart - Last 7 Days)
    const latencyClassifyMap: { [key: string]: { total: number, count: number } } = {};
    const latencySimilarityMap: { [key: string]: { total: number, count: number } } = {};

    // Init last 7 days
    for(let i=6; i>=0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0]; // YYYY-MM-DD
        activityMap[dateStr] = 0;
        latencyClassifyMap[dateStr] = { total: 0, count: 0 };
        latencySimilarityMap[dateStr] = { total: 0, count: 0 };
    }

    history.forEach(h => {
        if(h.timestamp) {
            const dateStr = new Date(h.timestamp).toISOString().split('T')[0];

            // Activity Count
            if(activityMap.hasOwnProperty(dateStr)) {
                activityMap[dateStr]++;
            }

            // Latency Accumulation
            if (h.metrics && h.metrics.inference_time) {
                if (h.type === 'Clasificación' && latencyClassifyMap.hasOwnProperty(dateStr)) {
                    latencyClassifyMap[dateStr].total += h.metrics.inference_time;
                    latencyClassifyMap[dateStr].count++;
                } else if (h.type === 'Similitud' && latencySimilarityMap.hasOwnProperty(dateStr)) {
                    latencySimilarityMap[dateStr].total += h.metrics.inference_time;
                    latencySimilarityMap[dateStr].count++;
                }
            }
        }
    });

    const lineLabels = Object.keys(activityMap); // Sorted
    const lineData = Object.values(activityMap);

    // Calculate daily averages for latency
    const latencyClassifyData = lineLabels.map(date => {
        const item = latencyClassifyMap[date];
        return item.count > 0 ? item.total / item.count : 0;
    });
    const latencySimilarityData = lineLabels.map(date => {
        const item = latencySimilarityMap[date];
        return item.count > 0 ? item.total / item.count : 0;
    });


    // --- RENDER PIE ---
    if (this.pieCanvas) {
      this.pieChart = new Chart(this.pieCanvas.nativeElement, {
        type: 'pie',
        data: {
          labels: pieLabels.length ? pieLabels : ['Sin Datos'],
          datasets: [{
            data: pieData.length ? pieData : [1],
            backgroundColor: [
              '#5d9cec', '#4fc1e9', '#48cfad', '#a0d468', '#ffce54', '#fc6e51', '#ed5565', '#ac92ec', '#ec87c0'
            ],
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
              legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } }
          }
        }
      });
    }

    // --- RENDER BAR ---
    if (this.barCanvas) {
      this.barChart = new Chart(this.barCanvas.nativeElement, {
        type: 'bar',
        data: {
          labels: bucketLabels,
          datasets: [{
            label: 'Frecuencia de Similitud',
            data: buckets,
            backgroundColor: '#48cfad',
            borderColor: '#37bc9b',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } }
          }
        }
      });
    }

    // --- RENDER LINE (Activity) ---
    if (this.lineCanvas) {
      this.lineChart = new Chart(this.lineCanvas.nativeElement, {
        type: 'line',
        data: {
          labels: lineLabels,
          datasets: [{
            label: 'Operaciones por Día',
            data: lineData,
            fill: true,
            borderColor: '#5d9cec',
            backgroundColor: 'rgba(93, 156, 236, 0.2)',
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } }
          }
        }
      });
    }

    // --- RENDER LINE (Latency Evolution) ---
    if (this.latencyCanvas) {
        this.latencyChart = new Chart(this.latencyCanvas.nativeElement, {
            type: 'line',
            data: {
                labels: lineLabels,
                datasets: [
                    {
                        label: 'Inferencia Clasificación (s)',
                        data: latencyClassifyData,
                        borderColor: '#ac92ec',
                        backgroundColor: 'rgba(172, 146, 236, 0.2)',
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Inferencia Similitud (s)',
                        data: latencySimilarityData,
                        borderColor: '#fc6e51',
                        backgroundColor: 'rgba(252, 110, 81, 0.2)',
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Segundos' }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(4) + ' s';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
  }

  refresh() {
      this.pieChart?.destroy();
      this.barChart?.destroy();
      this.lineChart?.destroy();
      this.latencyChart?.destroy();
      this.renderCharts();
  }
}

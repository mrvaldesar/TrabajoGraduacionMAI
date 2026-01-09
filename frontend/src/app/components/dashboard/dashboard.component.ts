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

  private pieChart: Chart | undefined;
  private barChart: Chart | undefined;
  private lineChart: Chart | undefined;

  totalOperations = 0;
  lastUpdate: Date = new Date();

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
  }

  renderCharts() {
    const rawHistory = localStorage.getItem('nlp_history');
    const history: any[] = rawHistory ? JSON.parse(rawHistory) : [];

    this.totalOperations = history.length;
    this.lastUpdate = new Date();

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
    // Init last 7 days with 0
    for(let i=6; i>=0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0]; // YYYY-MM-DD
        activityMap[dateStr] = 0;
    }

    history.forEach(h => {
        if(h.timestamp) {
            const dateStr = new Date(h.timestamp).toISOString().split('T')[0];
            if(activityMap.hasOwnProperty(dateStr)) {
                activityMap[dateStr]++;
            }
        }
    });

    const lineLabels = Object.keys(activityMap); // Already sorted by date construction
    const lineData = Object.values(activityMap);


    // --- RENDER PIE ---
    if (this.pieCanvas) {
      this.pieChart = new Chart(this.pieCanvas.nativeElement, {
        type: 'pie',
        data: {
          labels: pieLabels.length ? pieLabels : ['Sin Datos'],
          datasets: [{
            data: pieData.length ? pieData : [1], // Dummy data if empty
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

    // --- RENDER LINE ---
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
  }

  refresh() {
      this.pieChart?.destroy();
      this.barChart?.destroy();
      this.lineChart?.destroy();
      this.renderCharts();
  }
}

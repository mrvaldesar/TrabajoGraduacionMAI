import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-history',
  template: `
    <div class="card">
      <div class="card-header bg-secondary text-white">
        Historial Local de Operaciones
      </div>
      <div class="card-body">
        <div *ngIf="history.length === 0" class="text-muted text-center">
            No hay operaciones recientes.
        </div>

        <table *ngIf="history.length > 0" class="table table-striped">
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Archivo(s)</th>
                    <th>Resultado</th>
                </tr>
            </thead>
            <tbody>
                <tr *ngFor="let item of history">
                    <td>{{ item.timestamp | date:'short' }}</td>
                    <td>{{ item.type }}</td>
                    <td>{{ item.file }}</td>
                    <td>{{ item.result }}</td>
                </tr>
            </tbody>
        </table>

        <button *ngIf="history.length > 0" class="btn btn-outline-danger mt-3" (click)="clear()">
            Borrar Historial
        </button>
      </div>
    </div>
  `
})
export class HistoryComponent implements OnInit {
  history: any[] = [];

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory() {
    this.history = JSON.parse(localStorage.getItem('nlp_history') || '[]');
  }

  clear() {
    localStorage.removeItem('nlp_history');
    this.history = [];
  }
}

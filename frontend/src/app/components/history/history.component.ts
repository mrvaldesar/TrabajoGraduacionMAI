import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-history',
  template: `
    <div class="sap-window">
      <div class="sap-window-header">
        <span>Historial Local de Operaciones</span>
      </div>
      <div class="sap-window-body">
        <div *ngIf="history.length === 0" class="text-muted text-center">
            No hay operaciones recientes.
        </div>

        <table *ngIf="history.length > 0" class="sap-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Archivo(s)</th>
                    <th>Resultado</th>
                </tr>
            </thead>
            <tbody>
                <tr *ngFor="let item of history; let i = index">
                    <td style="width: 30px; text-align: center;">{{ i + 1 }}</td>
                    <td>{{ item.timestamp | date:'short' }}</td>
                    <td>{{ item.type }}</td>
                    <td>{{ item.file }}</td>
                    <td>{{ item.result }}</td>
                </tr>
            </tbody>
        </table>

        <div class="sap-form-row mt-3" *ngIf="history.length > 0">
             <button class="sap-btn" (click)="clear()">
                Borrar Historial
             </button>
        </div>
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

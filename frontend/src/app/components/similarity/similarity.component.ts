import { Component } from '@angular/core';
import { ApiService, SimilarityResponse } from '../../services/api.service';
import { FileConversionService } from '../../services/file-conversion.service';

@Component({
  selector: 'app-similarity',
  template: `
    <div class="sap-window">
      <div class="sap-window-header">
        <span>Similitud Semántica</span>
      </div>
      <div class="sap-window-body">
        <p style="margin-bottom: 20px; color: #555;">Compara dos documentos (PDF, DOCX, TXT, JPG, PNG) para verificar si son semánticamente similares o duplicados.</p>

        <div class="row">
          <div class="col-md-6 mb-3">
             <div class="sap-form-row">
                <label class="sap-label">Archivo 1</label>
                <input class="sap-input" type="file" (change)="onFile1Selected($event)">
             </div>
          </div>
          <div class="col-md-6 mb-3">
             <div class="sap-form-row">
                <label class="sap-label">Archivo 2</label>
                <input class="sap-input" type="file" (change)="onFile2Selected($event)">
             </div>
          </div>
        </div>

        <div class="sap-form-row">
             <button class="sap-btn sap-btn-primary" (click)="compare()" [disabled]="!file1 || !file2 || loading">
                {{ loading ? 'Procesando...' : 'Calcular Similitud' }}
             </button>
        </div>

        <div *ngIf="loading" class="mt-3">
            <p class="mb-1">{{ statusMessage }}</p>
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" role="progressbar" [style.width.%]="progress" [attr.aria-valuenow]="progress" aria-valuemin="0" aria-valuemax="100">
                    {{ progress }}%
                </div>
            </div>
        </div>

        <div *ngIf="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>

        <div *ngIf="result" class="alert mt-3" [ngClass]="result.is_duplicate ? 'alert-warning' : 'alert-info'" style="border: 1px solid #999;">
          <h4 class="alert-heading" style="font-size: 14px; font-weight: bold;">Resultado:</h4>
          <p class="mb-1"><strong>Puntaje de Similitud:</strong> {{ result.similarity | number:'1.4-4' }}</p>
          <p class="mb-0">
            <strong>Estado:</strong>
            <span *ngIf="result.is_duplicate" class="badge bg-danger ms-2">Posible Duplicado</span>
            <span *ngIf="!result.is_duplicate" class="badge bg-success ms-2">Diferentes</span>
          </p>
        </div>
      </div>
    </div>
  `
})
export class SimilarityComponent {
  file1: File | null = null;
  file2: File | null = null;
  result: SimilarityResponse | null = null;
  error: string | null = null;
  loading = false;
  progress = 0;
  statusMessage = '';

  constructor(
    private api: ApiService,
    private fileConversion: FileConversionService
  ) {}

  onFile1Selected(event: any) { this.file1 = event.target.files[0]; this.result = null; }
  onFile2Selected(event: any) { this.file2 = event.target.files[0]; this.result = null; }

  async compare() {
    if (!this.file1 || !this.file2) return;

    this.loading = true;
    this.error = null;
    this.result = null;
    this.progress = 0;
    this.statusMessage = 'Iniciando...';

    try {
        // Convert File 1
        this.statusMessage = `Procesando archivo 1 (${this.file1.name})...`;
        const onProgress1 = (status: string, percentage: number) => {
            this.statusMessage = `Archivo 1: ${status}`;
            // 0-40% total
            this.progress = Math.floor(percentage * 0.4);
        };
        const textFile1 = await this.fileConversion.convertToTxtFile(this.file1, onProgress1);

        // Convert File 2
        this.statusMessage = `Procesando archivo 2 (${this.file2.name})...`;
        const onProgress2 = (status: string, percentage: number) => {
            this.statusMessage = `Archivo 2: ${status}`;
            // 40-80% total
            this.progress = 40 + Math.floor(percentage * 0.4);
        };
        const textFile2 = await this.fileConversion.convertToTxtFile(this.file2, onProgress2);

        // Send to API
        this.statusMessage = 'Comparando documentos...';
        this.progress = 85;

        this.api.similarity(textFile1, textFile2).subscribe({
          next: (res) => {
            this.progress = 100;
            this.statusMessage = 'Completado';
            setTimeout(() => {
                this.loading = false;
                this.result = res;
                this.addToHistory({
                    type: 'Similitud',
                    file: `${this.file1?.name} vs ${this.file2?.name}`,
                    result: `Score: ${res.similarity.toFixed(4)}`,
                    timestamp: new Date()
                });
            }, 500);
          },
          error: (err) => {
            this.error = 'Error al comparar archivos. Verifica el servidor.';
            console.error(err);
            this.loading = false;
          }
        });

    } catch (error) {
        this.error = 'Error al convertir los archivos a texto.';
        console.error(error);
        this.loading = false;
    }
  }

  addToHistory(item: any) {
      const history = JSON.parse(localStorage.getItem('nlp_history') || '[]');
      history.unshift(item);
      localStorage.setItem('nlp_history', JSON.stringify(history));
  }
}

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
             <button *ngIf="extractedText1" class="sap-btn sap-btn-secondary mt-2" (click)="showExtractedText1 = !showExtractedText1">
                  {{ showExtractedText1 ? 'Ocultar Texto 1' : 'Ver Texto Extraído 1' }}
             </button>
             <div *ngIf="showExtractedText1 && extractedText1" class="mt-2 p-2" style="background: #f0f0f0; border: 1px solid #ccc; max-height: 200px; overflow-y: auto;">
                <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px; margin: 0;">{{ extractedText1 }}</pre>
             </div>
          </div>
          <div class="col-md-6 mb-3">
             <div class="sap-form-row">
                <label class="sap-label">Archivo 2</label>
                <input class="sap-input" type="file" (change)="onFile2Selected($event)">
             </div>
             <button *ngIf="extractedText2" class="sap-btn sap-btn-secondary mt-2" (click)="showExtractedText2 = !showExtractedText2">
                  {{ showExtractedText2 ? 'Ocultar Texto 2' : 'Ver Texto Extraído 2' }}
             </button>
             <div *ngIf="showExtractedText2 && extractedText2" class="mt-2 p-2" style="background: #f0f0f0; border: 1px solid #ccc; max-height: 200px; overflow-y: auto;">
                <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px; margin: 0;">{{ extractedText2 }}</pre>
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

          <hr *ngIf="metrics" style="border-top: 1px solid #999;">
          <div *ngIf="metrics" style="font-size: 12px;">
              <p class="mb-0"><strong>Tiempos de Ejecución:</strong></p>
              <ul class="mb-0 ps-3">
                  <li>Total (Cliente+Servidor): {{ metrics.total_time | number:'1.3-3' }} s</li>
                  <li>Respuesta Servidor: {{ metrics.server_time | number:'1.3-3' }} s</li>
                  <li>Inferencia Modelo: {{ metrics.inference_time | number:'1.4-4' }} s</li>
                  <li>Anonimización: {{ metrics.anonymization_time | number:'1.4-4' }} s</li>
              </ul>
          </div>
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

  extractedText1: string | null = null;
  extractedText2: string | null = null;
  showExtractedText1 = false;
  showExtractedText2 = false;

  // Metrics
  metrics: any = null;
  startTime = 0;

  constructor(
    private api: ApiService,
    private fileConversion: FileConversionService
  ) {}

  onFile1Selected(event: any) {
    this.file1 = event.target.files[0];
    this.result = null;
    this.metrics = null;
    this.extractedText1 = null;
    this.showExtractedText1 = false;
  }
  onFile2Selected(event: any) {
    this.file2 = event.target.files[0];
    this.result = null;
    this.metrics = null;
    this.extractedText2 = null;
    this.showExtractedText2 = false;
  }

  async compare() {
    if (!this.file1 || !this.file2) return;

    this.loading = true;
    this.error = null;
    this.result = null;
    this.metrics = null;
    this.progress = 0;
    this.statusMessage = 'Iniciando...';
    this.startTime = performance.now();

    try {
        // Convert File 1
        this.statusMessage = `Procesando archivo 1 (${this.file1.name})...`;
        const onProgress1 = (status: string, percentage: number) => {
            this.statusMessage = `Archivo 1: ${status}`;
            // 0-40% total
            this.progress = Math.floor(percentage * 0.4);
        };
        const textFile1 = await this.fileConversion.convertToTxtFile(this.file1, onProgress1);
        this.extractedText1 = await textFile1.text();

        // Convert File 2
        this.statusMessage = `Procesando archivo 2 (${this.file2.name})...`;
        const onProgress2 = (status: string, percentage: number) => {
            this.statusMessage = `Archivo 2: ${status}`;
            // 40-80% total
            this.progress = 40 + Math.floor(percentage * 0.4);
        };
        const textFile2 = await this.fileConversion.convertToTxtFile(this.file2, onProgress2);
        this.extractedText2 = await textFile2.text();

        // Send to API
        this.statusMessage = 'Comparando documentos...';
        this.progress = 85;
        const serverStart = performance.now();

        this.api.similarity(textFile1, textFile2).subscribe({
          next: (res) => {
            const serverEnd = performance.now();
            const totalEnd = performance.now();

            const serverTime = (serverEnd - serverStart) / 1000;
            const totalTime = (totalEnd - this.startTime) / 1000;

            this.metrics = {
                server_time: serverTime,
                total_time: totalTime,
                inference_time: res.inference_time,
                anonymization_time: res.anonymization_time
            };

            this.progress = 100;
            this.statusMessage = 'Completado';
            setTimeout(() => {
                this.loading = false;
                this.result = res;
                this.addToHistory({
                    type: 'Similitud',
                    file: `${this.file1?.name} vs ${this.file2?.name}`,
                    result: `Score: ${res.similarity.toFixed(4)}`,
                    timestamp: new Date(),
                    metrics: this.metrics,
                    anonymized_text: `Archivo 1: ${this.file1?.name}\n====================\n${res.anonymized_text_1}\n\nArchivo 2: ${this.file2?.name}\n====================\n${res.anonymized_text_2}`
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
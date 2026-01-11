import { Component } from '@angular/core';
import { ApiService, ClassificationResponse } from '../../services/api.service';
import { FileConversionService } from '../../services/file-conversion.service';

@Component({
  selector: 'app-classify',
  template: `
    <div class="sap-window">
      <div class="sap-window-header">
        <span>Clasificación de Documentos</span>
      </div>
      <div class="sap-window-body">
        <p style="margin-bottom: 20px; color: #555;">Sube un documento (PDF, DOCX, TXT, JPG, PNG) para que el modelo BETO identifique su categoría.</p>

        <div class="sap-form-row">
          <label for="fileInput" class="sap-label">Seleccionar archivo</label>
          <input class="sap-input" type="file" id="fileInput" (change)="onFileSelected($event)">
        </div>

        <div class="sap-form-row">
            <div class="sap-label"></div> <!-- Spacer for alignment -->
            <div style="display: flex; gap: 10px;">
                <button class="sap-btn sap-btn-primary" (click)="upload()" [disabled]="!selectedFile || loading">
                  {{ loading ? 'Procesando...' : 'Clasificar' }}
                </button>
                <button *ngIf="extractedText" class="sap-btn sap-btn-secondary" (click)="showExtractedText = !showExtractedText">
                  {{ showExtractedText ? 'Ocultar Texto' : 'Ver Texto Extraído' }}
                </button>
            </div>
        </div>

        <div *ngIf="showExtractedText && extractedText" class="mt-3 p-2" style="background: #f0f0f0; border: 1px solid #ccc; max-height: 200px; overflow-y: auto;">
             <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px; margin: 0;">{{ extractedText }}</pre>
        </div>

        <div *ngIf="loading" class="mt-3">
            <p class="mb-1">{{ statusMessage }}</p>
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" [style.width.%]="progress" [attr.aria-valuenow]="progress" aria-valuemin="0" aria-valuemax="100">
                    {{ progress }}%
                </div>
            </div>
        </div>

        <div *ngIf="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>

        <div *ngIf="result" class="alert alert-success mt-3" style="border: 1px solid #999; background: #e0ffd4; color: #000;">
          <h4 class="alert-heading" style="font-size: 14px; font-weight: bold;">Resultado:</h4>
          <p class="mb-1"><strong>Categoría:</strong> {{ result.category }}</p>
          <p class="mb-0"><strong>Confianza:</strong> {{ (result.confidence * 100) | number:'1.2-2' }}%</p>

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
export class ClassifyComponent {
  selectedFile: File | null = null;
  result: ClassificationResponse | null = null;
  error: string | null = null;
  loading = false;
  progress = 0;
  statusMessage = '';

  extractedText: string | null = null;
  showExtractedText = false;

  // Metrics
  metrics: any = null;
  startTime = 0;

  constructor(
    private api: ApiService,
    private fileConversion: FileConversionService
  ) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.result = null;
    this.error = null;
    this.progress = 0;
    this.statusMessage = '';
    this.metrics = null;
    this.extractedText = null;
    this.showExtractedText = false;
  }

  async upload() {
    if (!this.selectedFile) return;

    this.loading = true;
    this.error = null;
    this.result = null;
    this.metrics = null;
    this.progress = 5;
    this.statusMessage = 'Iniciando proceso...';
    this.startTime = performance.now();

    try {
      this.statusMessage = 'Preparando archivo...';

      // Callback to update progress from the service
      const onProgress = (status: string, percentage: number) => {
        this.statusMessage = status;
        // Map 0-100 from service to 0-60 in overall progress (leaving 40% for API call)
        this.progress = Math.floor(percentage * 0.6);
      };

      const textFile = await this.fileConversion.convertToTxtFile(this.selectedFile, onProgress);
      this.extractedText = await textFile.text();

      this.statusMessage = 'Enviando a modelo BETO...';
      this.progress = 60;
      const serverStart = performance.now();

      this.api.classify(textFile).subscribe({
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
                  type: 'Clasificación',
                  file: this.selectedFile?.name,
                  result: res.category,
                  timestamp: new Date(),
                  metrics: this.metrics,
                  anonymized_text: res.anonymized_text
              });
          }, 500);
        },
        error: (err) => {
          this.error = 'Error al procesar el archivo. Verifica el servidor.';
          console.error(err);
          this.loading = false;
        }
      });
    } catch (error) {
      this.error = 'Error al convertir el archivo a texto.';
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

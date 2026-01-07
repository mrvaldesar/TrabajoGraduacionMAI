import { Component } from '@angular/core';
import { ApiService, ClassificationResponse } from '../../services/api.service';
import { FileConversionService } from '../../services/file-conversion.service';

@Component({
  selector: 'app-classify',
  template: `
    <div class="card">
      <div class="card-header bg-primary text-white">
        Clasificación de Documentos
      </div>
      <div class="card-body">
        <p class="card-text">Sube un documento (PDF, DOCX, TXT, JPG, PNG) para que el modelo BETO identifique su categoría.</p>

        <div class="mb-3">
          <label for="fileInput" class="form-label">Seleccionar archivo</label>
          <input class="form-control" type="file" id="fileInput" (change)="onFileSelected($event)">
        </div>

        <button class="btn btn-primary" (click)="upload()" [disabled]="!selectedFile || loading">
          {{ loading ? 'Procesando...' : 'Clasificar' }}
        </button>

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

        <div *ngIf="result" class="alert alert-success mt-3">
          <h4 class="alert-heading">Resultado:</h4>
          <p><strong>Categoría:</strong> {{ result.category }}</p>
          <p><strong>Confianza:</strong> {{ (result.confidence * 100) | number:'1.2-2' }}%</p>
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
  }

  async upload() {
    if (!this.selectedFile) return;

    this.loading = true;
    this.error = null;
    this.result = null;
    this.progress = 5;
    this.statusMessage = 'Iniciando proceso...';

    try {
      this.statusMessage = 'Preparando archivo...';

      // Callback to update progress from the service
      const onProgress = (status: string, percentage: number) => {
        this.statusMessage = status;
        // Map 0-100 from service to 0-60 in overall progress (leaving 40% for API call)
        this.progress = Math.floor(percentage * 0.6);
      };

      const textFile = await this.fileConversion.convertToTxtFile(this.selectedFile, onProgress);

      this.statusMessage = 'Enviando a modelo BETO...';
      this.progress = 60;

      this.api.classify(textFile).subscribe({
        next: (res) => {
          this.progress = 100;
          this.statusMessage = 'Completado';
          setTimeout(() => {
              this.loading = false;
              this.result = res;
              this.addToHistory({
                  type: 'Clasificación',
                  file: this.selectedFile?.name,
                  result: res.category,
                  timestamp: new Date()
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

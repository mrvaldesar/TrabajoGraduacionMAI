import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface ModelMetadata {
  name: string;
  type: string;
  description: string;
  path: string;
  metadata: { [key: string]: any };
}

@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.css']
})
export class ModelsComponent implements OnInit {
  models: ModelMetadata[] = [];
  loading = true;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchModels();
  }

  fetchModels(): void {
    this.loading = true;
    this.http.get<{ models: ModelMetadata[] }>(`${environment.apiUrl}/models`).subscribe({
      next: (response) => {
        this.models = response.models;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching models:', err);
        this.error = 'No se pudo cargar la información de los modelos. Verifica que el backend esté en ejecución.';
        this.loading = false;
      }
    });
  }

  // Helper to format metadata keys for display
  formatKey(key: string): string {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  // Helper to safely display values (handle objects/arrays)
  formatValue(value: any): string {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  getLabels(value: any): string[] {
      if (Array.isArray(value)) {
          return value;
      }
      return [];
  }
}

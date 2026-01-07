import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ClassificationResponse {
  category: string;
  confidence: number;
}

export interface SimilarityResponse {
  similarity: number;
  is_duplicate: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  classify(file: File): Observable<ClassificationResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ClassificationResponse>(`${this.apiUrl}/classify`, formData);
  }

  similarity(file1: File, file2: File): Observable<SimilarityResponse> {
    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);
    return this.http.post<SimilarityResponse>(`${this.apiUrl}/similarity`, formData);
  }
}

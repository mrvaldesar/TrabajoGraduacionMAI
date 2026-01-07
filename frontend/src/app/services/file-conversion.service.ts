import { Injectable } from '@angular/core';
import * as pdfjsLib from 'pdfjs-dist';
import * as mammoth from 'mammoth';
import * as Tesseract from 'tesseract.js';

// Configurar worker para pdfjs
(pdfjsLib as any).GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

export type ProgressCallback = (status: string, percentage: number) => void;

@Injectable({
  providedIn: 'root'
})
export class FileConversionService {

  constructor() { }

  async convertToTxtFile(file: File, onProgress?: ProgressCallback): Promise<File> {
    const text = await this.extractTextFromFile(file, onProgress);
    const blob = new Blob([text], { type: 'text/plain' });
    return new File([blob], 'converted.txt', { type: 'text/plain' });
  }

  async extractTextFromFile(file: File, onProgress?: ProgressCallback): Promise<string> {
    const fileType = file.type;
    const fileName = file.name.toLowerCase();

    if (fileType === 'text/plain' || fileName.endsWith('.txt')) {
      if (onProgress) onProgress('Leyendo archivo de texto...', 50);
      const text = await this.readTextFile(file);
      if (onProgress) onProgress('Completado', 100);
      return text;
    } else if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
      return await this.extractTextFromPDF(file, onProgress);
    } else if (fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || fileName.endsWith('.docx')) {
      if (onProgress) onProgress('Extrayendo texto de DOCX...', 50);
      const text = await this.extractTextFromDOCX(file);
      if (onProgress) onProgress('Completado', 100);
      return text;
    } else if (fileType === 'image/jpeg' || fileType === 'image/png' || fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png')) {
      return await this.extractTextFromImage(file, onProgress);
    } else {
      throw new Error('Tipo de archivo no soportado. Solo se permiten TXT, PDF, DOCX, JPG y PNG.');
    }
  }

  private async readTextFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  }

  private async extractTextFromPDF(file: File, onProgress?: ProgressCallback): Promise<string> {
    if (onProgress) onProgress('Extrayendo texto del PDF...', 10);
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await (pdfjsLib as any).getDocument({ data: arrayBuffer }).promise;
    let text = '';

    // Attempt standard text extraction
    for (let i = 1; i <= pdf.numPages; i++) {
      if (onProgress) onProgress(`Extrayendo texto página ${i}/${pdf.numPages}...`, 10 + Math.floor((i / pdf.numPages) * 20));
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map((item: any) => item.str).join(' ') + '\n';
    }

    // Check if text is sufficient; if not, assume scanned and try OCR
    if (text.replace(/\s/g, '').length < 50) {
      if (onProgress) onProgress('Texto insuficiente detectado. Iniciando OCR...', 30);
      return await this.performOCR(pdf, onProgress);
    }

    if (onProgress) onProgress('Completado', 100);
    return text;
  }

  private async performOCR(pdf: any, onProgress?: ProgressCallback): Promise<string> {
    let text = '';
    const totalPages = pdf.numPages;

    // Initialize worker once
    const worker = await Tesseract.createWorker('spa+eng', 1, {
      logger: (m: any) => {
          // Optional logging
      }
    });

    try {
      for (let i = 1; i <= totalPages; i++) {
        if (onProgress) onProgress(`Realizando OCR en página ${i}/${totalPages}...`, 30 + Math.floor((i / totalPages) * 60));

        const page = await pdf.getPage(i);
        const viewport = page.getViewport({ scale: 1.5 }); // Higher scale for better OCR
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        if (context) {
            await page.render({ canvasContext: context, viewport: viewport }).promise;
            const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/png'));

            if (blob) {
               const result = await worker.recognize(blob);
               text += result.data.text + '\n';
            }
        }
      }
    } finally {
      await worker.terminate();
    }

    if (onProgress) onProgress('OCR Completado', 100);
    return text;
  }

  private async extractTextFromDOCX(file: File): Promise<string> {
    const arrayBuffer = await file.arrayBuffer();
    const result = await (mammoth as any).extractRawText({ arrayBuffer });
    return result.value;
  }

  private async extractTextFromImage(file: File, onProgress?: ProgressCallback): Promise<string> {
    if (onProgress) onProgress('Iniciando OCR en imagen...', 10);

    const result = await Tesseract.recognize(file, 'spa+eng', {
      logger: (m: any) => {
        if (m.status === 'recognizing text' && onProgress) {
          onProgress(`OCR: Reconociendo texto... ${(m.progress * 100).toFixed(0)}%`, 10 + (m.progress * 80));
        }
      }
    });

    if (onProgress) onProgress('Completado', 100);
    return result.data.text;
  }
}

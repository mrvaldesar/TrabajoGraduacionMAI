import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="sap-wrapper">
      <!-- Top Header -->
      <div class="sap-header">
        <span style="margin-right: 10px;">🔷</span>
        <span>SAP Business One | NLP Extension</span>
      </div>

      <div class="sap-container">
        <!-- Side Navigation (Modules) -->
        <nav class="sap-sidebar">
          <div style="padding: 10px; font-weight: bold; color: #555; text-transform: uppercase; font-size: 11px;">Módulos</div>

          <a class="sap-menu-item" routerLink="/classify" routerLinkActive="active">
            <i class="bi bi-file-earmark-text me-2"></i> Clasificación
          </a>

          <a class="sap-menu-item" routerLink="/similarity" routerLinkActive="active">
             <i class="bi bi-files me-2"></i> Similitud
          </a>

          <a class="sap-menu-item" routerLink="/history" routerLinkActive="active">
             <i class="bi bi-clock-history me-2"></i> Historial
          </a>
        </nav>

        <!-- Main Content Area -->
        <div class="sap-main">
          <router-outlet></router-outlet>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'nlp-frontend';
}

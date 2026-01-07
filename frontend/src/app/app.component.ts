import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="#">NLP API Service</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link" routerLink="/classify" routerLinkActive="active">Clasificación</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/similarity" routerLinkActive="active">Similitud</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/history" routerLinkActive="active">Historial</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'nlp-frontend';
}

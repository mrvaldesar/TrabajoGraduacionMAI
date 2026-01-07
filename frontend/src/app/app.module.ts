import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { ClassifyComponent } from './components/classify/classify.component';
import { SimilarityComponent } from './components/similarity/similarity.component';
import { HistoryComponent } from './components/history/history.component';

const routes: Routes = [
  { path: 'classify', component: ClassifyComponent },
  { path: 'similarity', component: SimilarityComponent },
  { path: 'history', component: HistoryComponent },
  { path: '', redirectTo: '/classify', pathMatch: 'full' }
];

@NgModule({
  declarations: [
    AppComponent,
    ClassifyComponent,
    SimilarityComponent,
    HistoryComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    RouterModule.forRoot(routes)
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

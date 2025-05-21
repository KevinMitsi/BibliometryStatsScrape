// src/app/services/stats.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private base = 'http://127.0.0.1:8001/stats';
  // private base = 'http://msvc-stats:8001/stats'; // dockerizado

  constructor(private http: HttpClient) {}

  // JSON endpoints
  getAuthors(): Observable<any> {
    return this.http.get(`${this.base}/authors`);
  }
  getTypes(): Observable<any> {
    return this.http.get(`${this.base}/types`);
  }
  getYearByType(): Observable<any> {
    return this.http.get(`${this.base}/year_by_type`);
  }
  getJournals(): Observable<any> {
    return this.http.get(`${this.base}/journals`);
  }
  getPublishers(): Observable<any> {
    return this.http.get(`${this.base}/publishers`);
  }
  getTermsByCategory(): Observable<any> {
    return this.http.get(`${this.base}/terms_by_category`);
  }
  

  // Plot endpoints (devuelven PNG)
  getAuthorsPlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/authors`, { responseType: 'blob' });
  }
  getTypesPlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/types`,    { responseType: 'blob' });
  }
  getYearByTypePlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/year_by_type`, { responseType: 'blob' });
  }
  getJournalsPlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/journals`, { responseType: 'blob' });
  }
  getPublishersPlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/publishers`, { responseType: 'blob' });
  }

  // Co-occurrence and wordcloud plots
  getCooccurrencePlot(): Observable<Blob> {
    return this.http.get(`http://127.0.0.1:8001/keywords/co-occurrence`, { responseType: 'blob' });
    // return this.http.get(`http://msvc-stats:8001/keywords/co-occurrence`, { responseType: 'blob' });
  }
  getWordcloudPlot(): Observable<Blob> {
    return this.http.get(`${this.base}/plot/wordcloud`, { responseType: 'blob' });
  }
}

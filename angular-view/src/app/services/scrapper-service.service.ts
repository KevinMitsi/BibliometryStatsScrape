
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ScrapperService {
  private base = 'http://127.0.0.1:8000'; //msvc no dockerizado
  // private base = 'http://host.docker.internal:8000';

  constructor(private http: HttpClient) {}

  postScrape(body: any): Observable<any> {
    return this.http.post(`${this.base}/scrape`, body);
  }

  getConvert(): Observable<any> {
    return this.http.get(`${this.base}/convert`);
  }

  getRepeated(): Observable<any> {
    return this.http.get(`${this.base}/repeated`);
  }
}

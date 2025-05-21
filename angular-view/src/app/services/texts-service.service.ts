import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface KeywordClustersResponse {
  [key: string]: string[];
}

@Injectable({
  providedIn: 'root'
})
export class TextsServiceService {
 private base = 'http://127.0.0.1:8003/texts';
//  private base = 'http://msvc-texts:8003/texts';  // dockerizado

  constructor(private http: HttpClient) {}

  getKeywordClusters(): Observable<KeywordClustersResponse> {
    return this.http.get<KeywordClustersResponse>(`${this.base}/findSimilar`);
  }
}
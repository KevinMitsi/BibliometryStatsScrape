import { Component, OnInit } from '@angular/core';
import { TextsServiceService, KeywordClustersResponse } from '../../services/texts-service.service';

interface Cluster {
  titles: string[];
  abstracts: string[];
}

@Component({
  selector: 'app-requerimiento4',
  templateUrl: './requerimiento4.component.html',
  styleUrls: ['./requerimiento4.component.css']
})
export class Requerimiento4Component implements OnInit {
  clusters: Cluster[] = [];
  viewMode: 'titles' | 'all' = 'titles';
  loading = false;
  error = '';

  constructor(private textsService: TextsServiceService) {}

  ngOnInit(): void {}

  loadClusters(): void {
    this.loading = true;
    this.error = '';
    this.clusters = [];

    this.textsService.getKeywordClusters().subscribe({
      next: (res: KeywordClustersResponse) => {
        for (const [key, abstracts] of Object.entries(res)) {
          const trimmed = key.replace(/^\[|\]$/g, '');
          const titles = trimmed.split(',').map(t => t.trim());
          this.clusters.push({ titles, abstracts });
        }
        this.loading = false;
      },
      error: err => {
        this.error = err.message || 'Error cargando clusters';
        this.loading = false;
      }
    });
  }

  setView(mode: 'titles' | 'all'): void {
    this.viewMode = mode;
  }
}
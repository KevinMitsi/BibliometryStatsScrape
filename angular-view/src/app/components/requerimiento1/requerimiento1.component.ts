import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { ScrapperService } from 'src/app/services/scrapper-service.service';

interface RepeatedArticleResponse {
  data?: RepeatedArticle[];
  status?: string;
}

interface RepeatedArticle {
  filename?: string;
  title?: string;
  hash?: string;
  timestamp?: string;
}

interface ScrapeResponse {
  status: string;
  data: Article[];
}

interface Article {
  shortDBName: string
  isiType: string
  mid: string
  language: string
  source: string
  bookEdition: string
  title: string
  pageEnd: string
  pageStart: string
  peerReviewed: string
  isOpenAccess: boolean
  publicationDate: string
  pageCount: string
  publisherLocations: []
  issue: string
  identifiers: []
  subjects: string[]
  abstract: string
  pubTypes: string
  an: string
  docTypes: string
  volume: string
  issns: string
  degreeLevel: string
  plink: string
  doids: []
  publisher: string
  contributors: string
  coverDate: string
  longDBName: string
  doi: string
}

@Component({
  selector: 'app-requerimiento1',
  templateUrl: './requerimiento1.component.html',
  styleUrls: ['./requerimiento1.component.css']
})
export class Requerimiento1Component {
  loading = false;
  error: string | null = null;
  myForm: FormGroup;
  articles: Article[] = [];

  additionalData: RepeatedArticle[] = [];
  loadingAdditional = false;
  additionalError: string | null = null;

  constructor(
    private scrapper: ScrapperService,
    private fb: FormBuilder,
  ) {
    this.myForm = this.fb.group({
      search_string: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      top_results: ['2', [Validators.required, Validators.min(2)]]
    });
  }

  onScrape() {
    if (this.myForm.invalid) {
      this.myForm.markAllAsTouched();
      return;
    }
    
    this.loading = true;
    this.error = null;
    this.articles = []; // Clear previous results

    const body = {
      search_string: this.myForm.get('search_string')?.value,
      email: this.myForm.get('email')?.value,
      password: this.myForm.get('password')?.value,
      top_results: this.myForm.get('top_results')?.value
    };

    console.log(body);

    this.scrapper.postScrape(body).subscribe({
      next: (response: ScrapeResponse) => {
        this.loading = false;
        this.articles = response.data;
        alert('¡Scrape finalizado con éxito!');
      },
      error: err => {
        this.loading = false;
        this.error = err.message || 'Error desconocido';
      }
    });
  }

  loadAdditionalData() {
  this.loadingAdditional = true;
  this.additionalError = null;
  
  this.scrapper.getRepeated().subscribe({
    next: (response: RepeatedArticleResponse) => {
      this.additionalData = response.data || (response as unknown as RepeatedArticle[]);
      this.loadingAdditional = false;
    },
    error: (err: Error) => {
      this.additionalError = err.message || 'Error loading additional data';
      this.loadingAdditional = false;
    }
  });
}

  showDetails(article: Article) {
    // This could be expanded to show details in a modal
    console.log('Article details:', article);
  }
}
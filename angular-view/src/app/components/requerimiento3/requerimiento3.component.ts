import { Component, OnInit } from '@angular/core';
import { StatsService } from '../../services/stats-service.service';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

interface TermsByCategoryResponse {
  status: string;
  categories: {
    [category: string]: {
      [term: string]: number;
    };
  };
}

interface CategoryTerm {
  category: string;
  term: string;
  count: number;
}

@Component({
  selector: 'app-requerimiento3',
  templateUrl: './requerimiento3.component.html',
  styleUrls: ['./requerimiento3.component.css']
})
export class Requerimiento3Component implements OnInit {
  cooccurrenceUrl?: SafeResourceUrl;
  wordcloudUrl?: SafeResourceUrl;
  loadingCooc = false;
  loadingWord = false;
  errorCooc = '';
  errorWord = '';

  categoryTerms: CategoryTerm[] = [];
  loadingTerms = false;
  errorTerms = '';
  displayedCategories: string[] = [];

  constructor(
    private stats: StatsService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    // No cargar automáticamente, se espera interacción del usuario
  }

  loadCooccurrence(): void {
    this.errorCooc = '';
    this.cooccurrenceUrl = undefined;
    this.loadingCooc = true;

    this.stats.getCooccurrencePlot().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        this.cooccurrenceUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
        this.loadingCooc = false;
      },
      error: err => {
        this.errorCooc = err.message || 'Error cargando co-ocurrencia';
        this.loadingCooc = false;
      }
    });
  }

  loadWordcloud(): void {
    this.errorWord = '';
    this.wordcloudUrl = undefined;
    this.loadingWord = true;

    this.stats.getWordcloudPlot().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        this.wordcloudUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
        this.loadingWord = false;
      },
      error: err => {
        this.errorWord = err.message || 'Error cargando wordcloud';
        this.loadingWord = false;
      }
    });
  }

  loadTermsByCategory(): void {
    this.errorTerms = '';
    this.categoryTerms = [];
    this.loadingTerms = true;

    this.stats.getTermsByCategory().subscribe({
      next: (response: TermsByCategoryResponse) => {
        if (response.status === 'ok') {
          // Convert nested object to flat array for table display
          const flatData: CategoryTerm[] = [];
          
          Object.entries(response.categories).forEach(([category, terms]) => {
            Object.entries(terms).forEach(([term, count]) => {
              flatData.push({ category, term, count });
            });
          });
          
          // Sort by category, then by count (descending), then by term (alphabetically)
          this.categoryTerms = flatData.sort((a, b) => 
            a.category.localeCompare(b.category) || b.count - a.count || a.term.localeCompare(b.term)
          );
          
          // Get unique category names
          this.displayedCategories = [...new Set(flatData.map(item => item.category))];
        } else {
          this.errorTerms = 'Error en la respuesta del servidor';
        }
        this.loadingTerms = false;
      },
      error: err => {
        this.errorTerms = err.message || 'Error cargando términos por categoría';
        this.loadingTerms = false;
      }
    });
  }
}
// src/app/requerimiento2/requerimiento2.component.ts
import { Component, OnInit } from '@angular/core';
import { StatsService }      from '../../services/stats-service.service';
import { StatConfig }        from '../stats-card/stats-card.component';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-requerimiento2',
  templateUrl: './requerimiento2.component.html',
  styleUrls: ['./requerimiento2.component.css']
})
export class Requerimiento2Component implements OnInit {
  configs: StatConfig[] = [];

  constructor(private stats: StatsService, private sanitizer: DomSanitizer) {}

  ngOnInit() {
    this.configs = [
      {
        label: 'Top Authors',
        loadingJson: false,
        loadingPlot: false,
        loadJson: () => {
          this.stats.getAuthors().subscribe({
            next: res => {
              this.configs[0].data = res.top_authors;
              this.configs[0].loadingJson = false;
            },
            error: err => {
              this.configs[0].errorJson = err.message || 'Error cargando autores';
              this.configs[0].loadingJson = false;
            }
          });
        },
        loadPlot: () => {
          this.stats.getAuthorsPlot().subscribe({
            next: blob => {
              const unsafeUrl = URL.createObjectURL(blob);
              this.configs[0].plotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
              this.configs[0].loadingPlot = false;
            },
            error: err => {
              this.configs[0].errorPlot = err.message || 'Error cargando gráfico';
              this.configs[0].loadingPlot = false;
            }
          });
        }
      },
      {
        label: 'By Type',
        loadingJson: false,
        loadingPlot: false,
        loadJson: () => {
          this.stats.getTypes().subscribe({
            next: res => {
              this.configs[1].data = res.by_type;
              this.configs[1].loadingJson = false;
            },
            error: err => {
              this.configs[1].errorJson = err.message || 'Error cargando tipos';
              this.configs[1].loadingJson = false;
            }
          });
        },
        loadPlot: () => {
          this.stats.getTypesPlot().subscribe({
            next: blob => {
              const unsafeUrl = URL.createObjectURL(blob);
              this.configs[1].plotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
              this.configs[1].loadingPlot = false;
            },
            error: err => {
              this.configs[1].errorPlot = err.message || 'Error cargando gráfico';
              this.configs[1].loadingPlot = false;
            }
          });
        }
      },
      {
        label: 'Year by Type',
        loadingJson: false,
        loadingPlot: false,
        loadJson: () => {
          this.stats.getYearByType().subscribe({
            next: res => {
              this.configs[2].data = res.year_by_type;
              this.configs[2].loadingJson = false;
            },
            error: err => {
              this.configs[2].errorJson = err.message || 'Error cargando año por tipo';
              this.configs[2].loadingJson = false;
            }
          });
        },
        loadPlot: () => {
          this.stats.getYearByTypePlot().subscribe({
            next: blob => {
              const unsafeUrl = URL.createObjectURL(blob);
              this.configs[2].plotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
              this.configs[2].loadingPlot = false;
            },
            error: err => {
              this.configs[2].errorPlot = err.message || 'Error cargando gráfico';
              this.configs[2].loadingPlot = false;
            }
          });
        }
      },
      {
        label: 'Top Journals',
        loadingJson: false,
        loadingPlot: false,
        loadJson: () => {
          this.stats.getJournals().subscribe({
            next: res => {
              this.configs[3].data = res.top_journals;
              this.configs[3].loadingJson = false;
            },
            error: err => {
              this.configs[3].errorJson = err.message || 'Error cargando revistas';
              this.configs[3].loadingJson = false;
            }
          });
        },
        loadPlot: () => {
          this.stats.getJournalsPlot().subscribe({
            next: blob => {
              const unsafeUrl = URL.createObjectURL(blob);
              this.configs[3].plotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
              this.configs[3].loadingPlot = false;
            },
            error: err => {
              this.configs[3].errorPlot = err.message || 'Error cargando gráfico';
              this.configs[3].loadingPlot = false;
            }
          });
        }
      },
      {
        label: 'Top Publishers',
        loadingJson: false,
        loadingPlot: false,
        loadJson: () => {
          this.stats.getPublishers().subscribe({
            next: res => {
              this.configs[4].data = res.top_publishers;
              this.configs[4].loadingJson = false;
            },
            error: err => {
              this.configs[4].errorJson = err.message || 'Error cargando editores';
              this.configs[4].loadingJson = false;
            }
          });
        },
        loadPlot: () => {
          this.stats.getPublishersPlot().subscribe({
            next: blob => {
              const unsafeUrl = URL.createObjectURL(blob);
              this.configs[4].plotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
              this.configs[4].loadingPlot = false;
            },
            error: err => {
              this.configs[4].errorPlot = err.message || 'Error cargando gráfico';
              this.configs[4].loadingPlot = false;
            }
          });
        }
      }
    ];
  }
}

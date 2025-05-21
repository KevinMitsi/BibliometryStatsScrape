import { Component, OnInit, Input } from '@angular/core';
import { StatsService }     from './../../services/stats-service.service';
import { SafeResourceUrl, SafeUrl } from '@angular/platform-browser';
export interface StatConfig {
  label: string;
  loadingJson: boolean;
  loadingPlot: boolean;
  data?: any;
  plotUrl?: string | SafeUrl | SafeResourceUrl;  // Updated to accept SafeUrl or SafeResourceUrl
  errorJson?: string;
  errorPlot?: string;
  loadJson: () => void;
  loadPlot: () => void;
}
@Component({
  selector: 'app-stats-card',
  templateUrl: './stats-card.component.html',
  styleUrls: ['./stats-card.component.css']
})
export class StatsCardComponent {
  @Input() config!: StatConfig;

  constructor(private stats: StatsService) {
  }

  // Funciones que el padre asigna pero esta clase las "envuelve" para
  // controlar estados y bindear resultados:
  onLoadJson() {
    this.config.loadingJson = true;
    this.config.errorJson   = undefined;
    this.config.data        = undefined;

    this.config.loadJson();
  }

  onLoadPlot() {
    this.config.loadingPlot = true;
    this.config.errorPlot   = undefined;
    this.config.plotUrl     = undefined;

    this.config.loadPlot();
  }
}

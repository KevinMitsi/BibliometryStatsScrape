import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Requerimiento1Component } from './requerimiento1/requerimiento1.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Requerimiento2Component } from './requerimiento2/requerimiento2.component';
import { StatsCardComponent } from './stats-card/stats-card.component';
import { Requerimiento3Component } from './requerimiento3/requerimiento3.component';
import { Requerimiento4Component } from './requerimiento4/requerimiento4.component';

@NgModule({
  declarations: [
    Requerimiento1Component,
    Requerimiento2Component,
    StatsCardComponent,
    Requerimiento3Component,
    Requerimiento4Component
  ],
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule
  ],
  exports: [ 
    Requerimiento1Component
  ]
})
export class ComponentsModule { }
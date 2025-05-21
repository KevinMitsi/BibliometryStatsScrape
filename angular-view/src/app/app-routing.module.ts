import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Requerimiento1Component } from './components/requerimiento1/requerimiento1.component';
import { Requerimiento2Component } from './components/requerimiento2/requerimiento2.component';
import { Requerimiento3Component } from './components/requerimiento3/requerimiento3.component';
import { Requerimiento4Component } from './components/requerimiento4/requerimiento4.component';

const routes: Routes = [
  { path: 'req1', component: Requerimiento1Component },
  {path: 'req2', component: Requerimiento2Component},
  {path: 'req3', component: Requerimiento3Component},
  {path: 'req4', component: Requerimiento4Component},
  {path: '**', redirectTo: '', pathMatch: 'full'},
  { path: '', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
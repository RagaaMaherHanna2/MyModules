import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SerialsBatchesComponent } from './serials-batches/serials-batches.component';
const routes: Routes = [
  { path: 'list', component: SerialsBatchesComponent },
 
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SerialsBatchesRoutingModule { }

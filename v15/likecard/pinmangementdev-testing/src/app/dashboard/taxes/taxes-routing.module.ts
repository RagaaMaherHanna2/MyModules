import { CreateTaxComponent } from './create-tax/create-tax.component';
import { ListTaxesComponent } from './list-taxes/list-taxes.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'create-tax', component: CreateTaxComponent },
  { path: 'list-taxes', component: ListTaxesComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class TaxesRoutingModule {}



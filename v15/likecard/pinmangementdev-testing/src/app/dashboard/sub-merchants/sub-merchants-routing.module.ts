import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SubMerchantsListComponent } from './sub-merchants-list/sub-merchants-list.component';
import { SubMerchantDetailsComponent } from './sub-merchant-details/sub-merchant-details.component';

const routes: Routes = [
  {
    path: "list",
    component: SubMerchantsListComponent,
  },
  {
    path: 'details/:id',
    component: SubMerchantDetailsComponent,
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SubMerchantRoutingModule { }

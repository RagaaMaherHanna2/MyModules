import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MerchantsListComponent } from './merchants-list/merchants-list.component';
import { MerchantDetailsComponent } from './merchant-details/merchant-details.component';

const routes: Routes = [
  {
    path: '',
    component: MerchantsListComponent,
  },
  {
    path: 'details/:id',
    component: MerchantDetailsComponent,
  },

];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class InvitesRoutingModule { }

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RedeemPageComponent } from './redeem-page/redeem-page.component';
import { CheckCodeComponent } from './check-code/check-code.component';
import { RedeemCodeComponent } from './redeem-code/redeem-code.component';

const routes: Routes = [
  {
    path: ':sp-hash/:product_sku',
    component: RedeemPageComponent,

    children: [
      {
        path: '',
        component: CheckCodeComponent,
      },
      {
        path: 'redeem-code/:product_type',
        component: RedeemCodeComponent,
      },
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class RedeemPageRoutingModule { }

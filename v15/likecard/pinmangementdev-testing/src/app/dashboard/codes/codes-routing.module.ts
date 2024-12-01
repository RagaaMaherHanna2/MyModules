import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CheckCodeComponent } from './check-code/check-code.component';
import { RedeemCodeComponent } from './redeem-code/redeem-code.component';

const routes: Routes = [
  {
    path: 'check',
    component: CheckCodeComponent,
  },
  {
    path: 'redeem',
    component: RedeemCodeComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class CodesRoutingModule {}

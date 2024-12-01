import { AvailablePackageListComponent } from './available-package-list/available-package-list.component';
import { AvailablePackagesComponent } from './available-packages/available-packages.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: 'product/list', component: AvailablePackageListComponent },
  { path: 'product/details/:id', component: AvailablePackagesComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class MerchantDashboardRoutingModule {}

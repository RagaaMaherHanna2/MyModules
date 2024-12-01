import { InviteMerchantComponent } from './invite-merchant/invite-merchant.component';
import { EditMerchantComponent } from './edit-merchant/edit-merchant.component';
import { PackageMerchantsComponent } from './package-merchants/package-merchants.component';
import { PackageReportComponent } from './package-report/package-report.component';
import { PackageDetailsComponent } from './package-details/package-details.component';
import { EditPackageComponent } from './edit-package/edit-package.component';
import { CreatePackageComponent } from './create-package/create-package.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ListPackageComponent } from './list-package/list-package.component';
import { AddVouchersComponent } from './add-vouchers/add-vouchers.component';

const routes: Routes = [
  { path: 'create', component: CreatePackageComponent },
  { path: 'details/:reference', component: PackageDetailsComponent },
  { path: 'edit/:reference', component: EditPackageComponent },
  { path: 'codes/:reference', component: PackageReportComponent },
  { path: 'merchants/:reference', component: PackageMerchantsComponent },
  {
    path: 'invite/edit/:product_id/:invite_id',
    component: EditMerchantComponent,
  },
  { path: 'invite_merchant/:reference', component: InviteMerchantComponent },
  { path: 'list', component: ListPackageComponent },
  { path: 'add-vouchers/:reference', component: AddVouchersComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PackageRoutingModule {}

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PackageWizardStepsComponent } from './package-wizard-steps/package-wizard-steps.component';
import { PackageWizardCreateComponent } from './package-wizard-create/package-wizard-create.component';
import { PackageWizardAddProductsComponent } from './package-wizard-add-products/package-wizard-add-products.component';
import { PackageWizardInviteMerchantsComponent } from './package-wizard-invite-merchants/package-wizard-invite-merchants.component';
import { PackageWizardSummaryComponent } from './package-wizard-summary/package-wizard-summary.component';

const routes: Routes = [
  {
    path: '',
    component: PackageWizardStepsComponent,
    children: [
      {
        path: 'create',
        component: PackageWizardCreateComponent,
      },
      {
        path: 'add-products',
        component: PackageWizardAddProductsComponent,
      },
      {
        path: 'invite-merchants',
        component: PackageWizardInviteMerchantsComponent,
      },
      {
        path: 'summary',
        component: PackageWizardSummaryComponent
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PackageWizardRoutingModule { }

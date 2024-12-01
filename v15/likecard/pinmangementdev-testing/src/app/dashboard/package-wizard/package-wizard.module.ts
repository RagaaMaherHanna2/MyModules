import { AccordionModule } from 'primeng/accordion';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ButtonModule } from 'primeng/button';
import { CalendarModule } from 'primeng/calendar';
import { CardModule } from 'primeng/card';
import { CommonModule } from '@angular/common';
import { DividerModule } from 'primeng/divider';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { NgModule } from '@angular/core';
import { PackageWizardAddProductsComponent } from './package-wizard-add-products/package-wizard-add-products.component';
import { PackageWizardCreateComponent } from './package-wizard-create/package-wizard-create.component';
import { PackageWizardInviteMerchantsComponent } from './package-wizard-invite-merchants/package-wizard-invite-merchants.component';
import { PackageWizardRoutingModule } from './package-wizard-routing.module';
import { PackageWizardService } from 'src/app/services/Package/package-wizard.service';
import { PackageWizardStepsComponent } from './package-wizard-steps/package-wizard-steps.component';
import { PackageWizardSummaryComponent } from './package-wizard-summary/package-wizard-summary.component';
import { ReactiveFormsModule } from '@angular/forms';
import { StepsModule } from 'primeng/steps';
import { CheckboxModule } from 'primeng/checkbox';
@NgModule({
  declarations: [
    PackageWizardInviteMerchantsComponent,
    PackageWizardCreateComponent,
    PackageWizardAddProductsComponent,
    PackageWizardSummaryComponent,
    PackageWizardStepsComponent,
  ],
  imports: [
    AccordionModule,
    AutoCompleteModule,
    ButtonModule,
    CalendarModule,
    CardModule,
    CheckboxModule,
    CommonModule,
    DividerModule,
    DropdownModule,
    InputTextModule,
    PackageWizardRoutingModule,
    ReactiveFormsModule,
    StepsModule,
  ],
  providers: [
    {
      provide: PackageWizardService,
    },
  ],
})
export class PackageWizardModule {}

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvitesRoutingModule } from './merchants-routing.module';
import { MerchantsListComponent } from './merchants-list/merchants-list.component';
import { MerchantDetailsComponent } from './merchant-details/merchant-details.component';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SharedModule } from 'src/app/shared/shared.module';
import { DialogModule } from 'primeng/dialog';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { DropdownModule } from 'primeng/dropdown';
import { CheckboxModule } from 'primeng/checkbox';
import { DividerModule } from 'primeng/divider';
import { RadioButtonModule } from 'primeng/radiobutton';
import { TooltipModule } from 'primeng/tooltip';
@NgModule({
  declarations: [MerchantsListComponent, MerchantDetailsComponent],
  imports: [
    ButtonModule,
    CardModule,
    CommonModule,
    InvitesRoutingModule,
    ProgressSpinnerModule,
    SharedModule,
    TableModule,
    DialogModule,
    FormsModule,
    ReactiveFormsModule,
    InputTextModule,
    PasswordModule,
    DropdownModule,
    CheckboxModule,
    DividerModule,
    RadioButtonModule,
    TooltipModule,
  ],
})
export class MerchantsModule {}

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RedeemPageRoutingModule } from './redeem-page-routing.module';
import { RedeemPageComponent } from './redeem-page/redeem-page.component';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { StepsModule } from 'primeng/steps';
import { CheckCodeComponent } from './check-code/check-code.component';
import { DividerModule } from 'primeng/divider';
import { RedeemCodeComponent } from './redeem-code/redeem-code.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { DropdownModule } from 'primeng/dropdown';
@NgModule({
  declarations: [
    RedeemPageComponent,
    CheckCodeComponent,
    RedeemCodeComponent
  ],
  imports: [
    CommonModule,
    RedeemPageRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    ButtonModule,
    CardModule,
    TableModule,
    StepsModule,
    DividerModule,
    ProgressSpinnerModule,
    DropdownModule
  ]
})
export class RedeemPageModule { }

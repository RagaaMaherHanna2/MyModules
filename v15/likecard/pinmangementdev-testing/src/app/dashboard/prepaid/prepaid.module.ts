import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PrepaidRoutingModule } from './prepaid-routing.module';
import { CheckBalanceComponent } from './check-balance/check-balance.component';

import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TabViewModule } from 'primeng/tabview';
import { TableModule } from 'primeng/table';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { OperationsHistoryComponent } from './operations-history/operations-history.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
@NgModule({
  declarations: [
    CheckBalanceComponent,
    OperationsHistoryComponent
  ],
  imports: [
    CommonModule,
    PrepaidRoutingModule,
    CardModule,
    InputTextModule,
    ButtonModule,
    TabViewModule,
    InputTextareaModule,
    TableModule,
    FormsModule,
    ReactiveFormsModule,
    ProgressSpinnerModule
    
  ]
})
export class PrepaidModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OrdersRoutingModule } from './orders-routing.module';
import { OrdersComponent } from './list-orders/orders.component';

import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { OrdersDetailsComponent } from './orders-details/orders-details.component';
import { CalendarModule } from 'primeng/calendar';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';

@NgModule({
  declarations: [
    OrdersComponent,
    OrdersDetailsComponent
  ],
  imports: [
    CommonModule,
    OrdersRoutingModule,
    CardModule,
    TableModule,
    InputTextModule,
    ButtonModule,
    ProgressSpinnerModule,
    TableModule,
    CalendarModule,
    ReactiveFormsModule,
    FormsModule,
    DropdownModule
  ]
})
export class OrdersModule { }

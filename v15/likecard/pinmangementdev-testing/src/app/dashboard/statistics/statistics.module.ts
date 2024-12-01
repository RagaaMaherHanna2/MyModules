import { NgModule } from '@angular/core';
import {
  CommonModule,
  CurrencyPipe,
  DatePipe,
  DecimalPipe,
} from '@angular/common';

import { StatisticsRoutingModule } from './statistics-routing.module';
import { StatisticsComponent } from './statistics/statistics.component';

import { AvatarModule } from 'primeng/avatar';
import { SummaryComponent } from './summary/summary.component';
import { ChartModule } from 'primeng/chart';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

@NgModule({
  declarations: [StatisticsComponent, SummaryComponent],
  imports: [
    AvatarModule,
    AvatarModule,
    ChartModule,
    CommonModule,
    DropdownModule,
    FormsModule,
    ReactiveFormsModule,
    StatisticsRoutingModule,
  ],
  providers: [DatePipe, CurrencyPipe, DecimalPipe],
})
export class StatisticsModule {}

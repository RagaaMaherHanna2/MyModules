import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { RedeemHistoryRoutingModule } from './redeem-history-routing.module';
import { RedeemHistoryComponent } from './redeem-history/redeem-history.component';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { RedeemHistoryDetailsComponent } from './redeem-history-details/redeem-history-details.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
@NgModule({
  declarations: [RedeemHistoryComponent, RedeemHistoryDetailsComponent],
  imports: [
    CommonModule,
    RedeemHistoryRoutingModule,
    CardModule,
    TableModule,
    InputTextModule,
    ButtonModule,
    ProgressSpinnerModule,
  ],
})
export class RedeemHistoryModule {}

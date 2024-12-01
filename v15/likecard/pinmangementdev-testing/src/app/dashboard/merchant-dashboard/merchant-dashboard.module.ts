import { TableModule } from 'primeng/table';
import { DialogModule } from 'primeng/dialog';
import { BadgeModule } from 'primeng/badge';
import { ButtonModule } from 'primeng/button';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MerchantDashboardRoutingModule } from './merchant-dashboard-routing.module';
import { AvailablePackagesComponent } from './available-packages/available-packages.component';
import { TabViewModule } from 'primeng/tabview';
import { DividerModule } from 'primeng/divider';
import { CarouselModule } from 'primeng/carousel';
import { InputTextModule } from 'primeng/inputtext';
import { AvailablePackageListComponent } from './available-package-list/available-package-list.component';


@NgModule({
  declarations: [AvailablePackagesComponent, AvailablePackageListComponent],
  imports: [
    CommonModule,
    MerchantDashboardRoutingModule,
    CardModule,
    FormsModule,
    ReactiveFormsModule,
    ButtonModule,
    BadgeModule,
    DialogModule,
    TabViewModule,
    DividerModule,
    CarouselModule,
    InputTextModule,
    TableModule,
  ],
})
export class MerchantDashboardModule {}

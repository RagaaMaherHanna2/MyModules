import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CodesRoutingModule } from './codes-routing.module';
import { CheckCodeComponent } from './check-code/check-code.component';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RedeemCodeComponent } from './redeem-code/redeem-code.component';
import { TabViewModule } from 'primeng/tabview';
import { FileUploadModule } from 'primeng/fileupload';
import { TableModule } from 'primeng/table';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { DropdownModule } from 'primeng/dropdown';


@NgModule({
  declarations: [CheckCodeComponent, RedeemCodeComponent],
  imports: [
    ButtonModule,
    CardModule,
    CodesRoutingModule,
    CommonModule,
    DropdownModule,
    FileUploadModule,
    FormsModule,
    InputTextModule,
    InputTextareaModule,
    ReactiveFormsModule,
    TabViewModule,
    TableModule
  ],
})
export class CodesModule {}

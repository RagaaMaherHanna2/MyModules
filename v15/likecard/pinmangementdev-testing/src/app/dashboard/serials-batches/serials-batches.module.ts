import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { SerialsBatchesRoutingModule } from './serials-batches-routing.module';
import { SerialsBatchesComponent } from './serials-batches/serials-batches.component';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [SerialsBatchesComponent],
  imports: [
    CommonModule,
    SerialsBatchesRoutingModule,
    TableModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    FormsModule,
  ],
})
export class SerialsBatchesModule {}

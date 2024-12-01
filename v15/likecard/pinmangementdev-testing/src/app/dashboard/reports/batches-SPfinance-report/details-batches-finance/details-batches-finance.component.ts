import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SerialsBatchesService } from 'src/app/services/serials-batches/serials-batches.service';
import { SerialFilter, SerialsBatch } from 'src/models/serial/model';

@Component({
  selector: 'app-details-batches-finance',
  templateUrl: './details-batches-finance.component.html',
  styleUrls: ['./details-batches-finance.component.scss'],
})
export class DetailsBatchesFinanceComponent {
  constructor(
    private activatedRoute: ActivatedRoute,
    private service: SerialsBatchesService
  ) {}
  serialFilter: SerialFilter;
  serialBatch: SerialsBatch;
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.serialFilter = {
        limit: 10,
        offset: 0,
        id: +params['id'],
        sorting: '',
        batch_sequence: '',
        create_date: '',
        product_name: '',
        vendor_name: '',
        invoice_ref: '',
        category_name: '',
        state: '',
      };
    });
    this.loadData();
  }
  loadData(): void {
    this.service.getBatchesList(this.serialFilter).subscribe((res) => {
      if (res.ok) {
        this.serialBatch = res.result.data[0];
      }
    });
  }
}

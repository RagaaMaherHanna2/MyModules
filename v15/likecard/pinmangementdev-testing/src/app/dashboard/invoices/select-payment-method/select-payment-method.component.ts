import { Component } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { Bill } from 'src/models/invoices/invoices.model';

@Component({
  selector: 'app-select-payment-method',
  templateUrl: './select-payment-method.component.html',
  styleUrls: ['./select-payment-method.component.scss']
})


export class SelectPaymentMethodComponent {

  bill: Bill;

  constructor(private formBuilder: FormBuilder,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private invoicesService: InvoicesService) { }
  selectPaymentForm = this.formBuilder.group({
    type: ['', [Validators.required]],

  });
  paymentMethods: { name: string; reference: string }[] = [{ name: $localize`Bank Transfer`, reference: 'invoice_payment' }];

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.invoicesService.getBills(0, 0,  Number(params['id'])).subscribe((res) => {
        if (res.ok) {
          this.bill = res.result.data[0];
        }
      });
    });
  }
  submit() {
    this.router.navigate([`/dashboard/invoices/bills/pay/${this.bill.id}/${this.selectPaymentForm.value.type}`]);
  }
}

import { CreateTax } from '../../../../models/Taxes/models';
import { TaxesService } from '../../../services/taxes/taxes.service';
import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormControl,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { MessageService } from 'primeng/api';


@Component({
  selector: 'app-create-report',
  templateUrl: './create-tax.component.html',
  styleUrls: ['./create-tax.component.scss'],
})
export class CreateTaxComponent {
  taxesForm = this.formBuilder.group({
    name: ['', [Validators.required]],
    amount_type: ['', [Validators.required]],
    amount: [0, [Validators.required]],
  });

  amountTypeOptions: { name: string; value: string}[] = [
    { name: $localize`Fixed Amount`, value: 'fixed'},
    { name: $localize`Percentage`, value: 'percent'},
  ];

  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private store:Store,
    private taxesService: TaxesService,
    private messageService: MessageService,
  ) {}



  submit(): void {
    this.store.dispatch(openLoadingDialog());
    const requestBody: CreateTax = {
      name:this.taxesForm.value.name ? this.taxesForm.value.name : '',
      amount_type:this.taxesForm.value.amount_type ? this.taxesForm.value.amount_type : '',
      amount:this.taxesForm.value.amount ? this.taxesForm.value.amount : 0,
    }
    this.taxesService.CreateTax(requestBody).subscribe((res: any) =>
      {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.router.navigate(['/dashboard/taxes/list-taxes'])
        }
      })
  }


}


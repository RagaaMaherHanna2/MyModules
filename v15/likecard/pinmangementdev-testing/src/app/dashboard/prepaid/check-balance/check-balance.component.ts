import { Component } from '@angular/core';
import { FormArray, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { CodeService } from 'src/app/services/Code/code.service';
import { prepaidCheckBalanceRequest } from 'src/models/prepaid/models';
import { PrepaidCode } from 'src/models/prepaid/models';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-check-balance',
  templateUrl: './check-balance.component.html',
  styleUrls: ['./check-balance.component.scss']
})
export class CheckBalanceComponent {

  prepaidCodes: PrepaidCode[];
  locale = $localize.locale;
  codesForm = this.formBuilder.group({
    codes: this.formBuilder.array([]),
  });

  constructor(
    private store: Store,
    private formBuilder: FormBuilder,
    private codeService: CodeService,
    private router: Router
  ) { }

  get codes() {
    return this.codesForm.controls['codes'] as FormArray;
  }
  ngOnInit() {
    this.addSerialCode();
  }
  onSubmit(event: SubmitEvent): void {
    let params: prepaidCheckBalanceRequest = {
      lines: this.codes.value,
      language: this.locale === 'ar-AE' ? 'ar' : 'en',
    }
    event.preventDefault();
    this.store.dispatch(openLoadingDialog());
    this.codeService
      .checkPrepaidCodesBalance(params)
      .subscribe((res) => {
        if (res.ok) {
          this.prepaidCodes = res.result;
          this.store.dispatch(closeLoadingDialog());
        }
      });
  }
  deleteRow(rowIndex: number): void {
    this.codes.removeAt(rowIndex);
  }
  addSerialCode(): void {
    const formRow = this.formBuilder.group({
      code: ['', [Validators.required]],
      pin_code: ['', [Validators.required]],
    });
    this.codes.push(formRow);
  }

  viewOperationsHistory(item: PrepaidCode) {
    this.router.navigate(['dashboard/prepaid/history/', item.code]);
  }
  disableAddButton() {
    return !this.codes.valid;
  }
}


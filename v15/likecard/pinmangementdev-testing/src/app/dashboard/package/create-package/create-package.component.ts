import { BaseResponse } from './../../../../models/responses/base-response.model';
import { PackageService } from './../../../services/Package/package.service';
import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';
import {
  CreatePackage,
  CodeType,
  CodeSeparator,
} from './../../../../models/package/models';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-create-package',
  templateUrl: './create-package.component.html',
  styleUrls: ['./create-package.component.scss'],
  providers: [MessageService],
})
export class CreatePackageComponent implements OnInit {
  package: CreatePackage = {} as CreatePackage;
  minDate: Date = new Date();
  codesTypes = [
    { name: 'alphanumeric', label: 'alphanumeric' },
    { name: 'numeric', label: 'numeric' },
    { name: 'alpha', label: 'alpha' },
  ];
  codeSeparators = [
    { name: '-', label: 'Dash (-)' },
    { name: '', label: 'Nothing' },
  ];
  createPackageForm = this.formBuilder.group({
    name: ['', [Validators.required]],
    name_ar: ['', [Validators.required]],
    expiration: [
      new Date(
        new Date(this.minDate.setHours(this.minDate.getHours() + 1)).setMinutes(
          0,
          0,
          0
        )
      ),
      [Validators.required],
    ],
    code_type: ['', [Validators.required]],
    code_separator: ['', [Validators.required]],
    code_days_duration: [0, [Validators.required]],
    code_hours_duration: [0, [Validators.required]],
  });
  submitted: boolean = false;
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private packageService: PackageService,
    private readonly store: Store<{}>
  ) {}

  ngOnInit(): void {}
  submit(event: SubmitEvent) {
    event.preventDefault();
    this.submitted = true;
    let value = this.createPackageForm.value;
    this.package.package_name = value.name as string;
    this.package.package_name_ar = value.name_ar as string;
    this.package.expiry_date = value.expiration!.toISOString();
    this.package.code_type = value.code_type
      ? (value.code_type as CodeType)
      : CodeType.alpha;
    this.package.code_separator = value.code_separator
      ? (value.code_separator as CodeSeparator)
      : CodeSeparator.dash;
    this.package.code_days_duration = value.code_days_duration ?? 0;
    this.package.code_hours_duration = value.code_hours_duration ?? 0;
    this.store.dispatch(openLoadingDialog());
    this.packageService.add(this.package).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`You Package is ready you can now create a generation requests and invite merchants`,
          life: 3000,
        });
        this.router.navigate(['dashboard/package/list']);
      } else {
        this.messageService.add({
          severity: 'error',
          summary: $localize`Adding Package Failed`,
          detail: res.message,
          life: 3000,
        });
      }
    });
  }
  isSubmitButtonDisabled() {
    return false;
  }
}

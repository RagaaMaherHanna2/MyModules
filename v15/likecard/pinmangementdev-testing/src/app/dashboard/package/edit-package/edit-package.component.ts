import { GetListResponse } from './../../../../models/responses/get-response.model';
import { BaseResponse } from './../../../../models/responses/base-response.model';
import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';
import { Store } from '@ngrx/store';
import { PackageService } from './../../../services/Package/package.service';
import { MessageService } from 'primeng/api';
import { Router, ActivatedRoute } from '@angular/router';
import { Validators, FormBuilder } from '@angular/forms';
import {
  CreatePackage,
  CodeType,
  CodeSeparator,
} from './../../../../models/package/models';
import { Component, OnInit } from '@angular/core';
import {
  getFormattedDateTime,
  getISODate,
  getLocaleString,
} from 'src/app/shared/utils/date';

@Component({
  selector: 'app-edit-package',
  templateUrl: './edit-package.component.html',
  styleUrls: ['./edit-package.component.scss'],
  providers: [MessageService],
})
export class EditPackageComponent implements OnInit {
  package: CreatePackage = {} as CreatePackage;
  locale = $localize.locale;
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
  editPackageForm = this.formBuilder.group({
    name: ['', [Validators.required]],
    name_ar: ['', [Validators.required]],
    expiration: [new Date(), [Validators.required]],
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
    private activatedRoute: ActivatedRoute,
    private readonly store: Store<{}>
  ) {}
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      let input: any = { reference: id['reference'] };
      this.packageService
        .details(input)
        .subscribe((res: BaseResponse<GetListResponse<CreatePackage>>) => {
          this.package = res.result.data[0];
          this.editPackageForm.patchValue({
            code_days_duration: this.package.code_days_duration,
            code_hours_duration: this.package.code_hours_duration,
            code_separator: this.package.code_separator,
            code_type: this.package.code_type,
            expiration: new Date(this.package.expiry_date ?? ''),
            name: this.package.package_name,
            name_ar: this.package.package_name_ar,
          });
        });
    });
  }
  submit() {
    this.submitted = true;
    let value = this.editPackageForm.value;
    this.package.package_name = value.name as string;
    this.package.package_name_ar = value.name_ar as string;
    this.package.expiry_date = getISODate(value.expiration ?? new Date());
    this.package.code_type = value.code_type as CodeType;
    this.package.code_separator = value.code_separator as CodeSeparator;
    this.package.code_days_duration = value.code_days_duration ?? 0;
    this.package.code_hours_duration = value.code_hours_duration ?? 0;
    this.store.dispatch(openLoadingDialog());
    this.packageService.edit(this.package).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`Package edited successfully`,
          life: 3000,
        });
        this.router.navigate(['dashboard/package/list']);
      } else {
        this.messageService.add({
          severity: 'error',
          summary: $localize`Edit Package Failed`,
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

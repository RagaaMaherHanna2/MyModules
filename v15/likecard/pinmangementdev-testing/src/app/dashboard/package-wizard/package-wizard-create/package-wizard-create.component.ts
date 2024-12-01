import { Component, OnInit } from '@angular/core';
import { Validators, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { PackageWizardService } from 'src/app/services/Package/package-wizard.service';
import { CreatePackage, CodeType, CodeSeparator } from 'src/models/package/models';

@Component({
  selector: 'app-package-wizard-create',
  templateUrl: './package-wizard-create.component.html',
  styleUrls: ['./package-wizard-create.component.scss']
})
export class PackageWizardCreateComponent implements OnInit {
  package: CreatePackage = {} as CreatePackage;
  minDate: Date = new Date();
  codesTypes = [
    { name: 'alphanumeric', label: 'Alpha-Numeric' },
    { name: 'numeric', label: 'Numeric' },
    { name: 'alpha', label: 'Alpha' },
  ];
  codeSeparators = [
    { name: '-', label: 'Dash (-)' },
    { name: '', label: 'Nothing' },
  ];
  createPackageForm = this.formBuilder.nonNullable.group({
    package_name: ['', [Validators.required]],
    package_name_ar: ['', [Validators.required]],
    expiry_date: [
      new Date(
        new Date(this.minDate.setHours(this.minDate.getHours() + 1)).setMinutes(
          0,
          0,
          0
        )
      ),
      [Validators.required],
    ],
    code_type: [CodeType.alphanumeric, [Validators.required]],
    code_separator: [CodeSeparator.dash, Validators.required],
    code_days_duration: [90, [Validators.required]],
    code_hours_duration: [0, [Validators.required]],
  });
  submitted: boolean = false;
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private packageWizardService: PackageWizardService,
  ) { }

  ngOnInit(): void {
    if (this.packageWizardService.package) {
      this.createPackageForm.setValue({ ...this.packageWizardService.package!, expiry_date: new Date(this.packageWizardService.package.expiry_date) })
      this.createPackageForm.markAllAsTouched();
    }
  }

  next(): void {

    this.packageWizardService.package = {
      package_name: this.createPackageForm.value.package_name!,
      package_name_ar: this.createPackageForm.value.package_name_ar!,
      expiry_date: this.createPackageForm.value.expiry_date!.toISOString(),
      code_days_duration: this.createPackageForm.value.code_days_duration!,
      code_hours_duration: this.createPackageForm.value.code_hours_duration!,
      code_separator: this.createPackageForm.value.code_separator!,
      code_type: this.createPackageForm.value.code_type!,
    };
    this.router.navigate(['/dashboard/package-wizard/add-products'])

  }

}

import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PackageWizardService } from 'src/app/services/Package/package-wizard.service';
import { Router } from '@angular/router';
import { UserService } from 'src/app/services/User/user.service';

@Component({
  selector: 'app-package-wizard-invite-merchants',
  templateUrl: './package-wizard-invite-merchants.component.html',
  styleUrls: ['./package-wizard-invite-merchants.component.scss'],
})
export class PackageWizardInviteMerchantsComponent implements OnInit {
  selectedMerchants: string[] = [];

  minDate = new Date();
  readonly errorMessage: string = $localize`Merchant reference is incorrect`;
  readonly initMessage: string = $localize`Enter a reference`;
  statuses: {
    loading: boolean;
    hit: boolean;
  }[] = [
    {
      loading: false,
      hit: false,
    },
  ];

  nextDisabled: boolean = false;

  //BEGIN Form Array
  inviteMerchantForm = this.formBuilder.group({
    invites: this.formBuilder.array([
      this.formBuilder.group({
        merchant: ['', Validators.required],
        price: [0, [Validators.required, Validators.min(1)]],
        limit: [0, [Validators.required, Validators.min(1)]],
        expiry_date: [new Date(), [Validators.required]],
      }),
    ]),
  });

  get invites() {
    return this.inviteMerchantForm.controls['invites'] as FormArray<FormGroup>;
  }
  //END Form Array

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserService,
    private packageWizardService: PackageWizardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (!this.packageWizardService.package) {
      this.router.navigate(['/dashboard/package-wizard/create']);
    }
    if (!this.packageWizardService.products) {
      this.router.navigate(['/dashboard/package-wizard/add-products']);
    }

    if (this.packageWizardService.merchants) {
      this.statuses[0].hit = true;
      for (let i = 0; i < this.packageWizardService.merchants.length - 1; i++) {
        this.addMerchant(true);
      }
      this.invites.setValue(this.packageWizardService.merchants);
      this.invites.markAllAsTouched();
      this.selectedMerchants = [
        ...this.packageWizardService.invitedMerchantsNames,
      ];
    }
  }

  addMerchant(hit: boolean = false): void {
    const formRow = this.formBuilder.group({
      merchant: ['', Validators.required],
      price: [0, [Validators.required, Validators.min(1)]],
      limit: [0, [Validators.required, Validators.min(1)]],
      expiry_date: [
        new Date(
          new Date(
            this.minDate.setHours(this.minDate.getHours() + 1)
          ).setMinutes(0, 0, 0)
        ),
        [Validators.required],
      ],
    });
    this.statuses.push({
      loading: false,
      hit: false,
    });
    this.invites.push(formRow);
  }

  deleteMerchant(index: number): void {
    this.invites.removeAt(index);
    this.statuses.splice(index, 1);
    this.selectedMerchants.splice(index, 1);
  }

  checkForDuplication(value: string, index: number): boolean {
    for (let i = this.invites.controls.length; i > 0; i--) {
      if (
        this.invites.controls[i - 1].value['merchant'] === value &&
        i - 1 !== index
      ) {
        this.invites.controls[index].controls['merchant'].setErrors({
          duplicated: true,
        });
        this.statuses[index].hit = false;

        return true;
      }
    }
    return false;
  }
  getMerchant(event: any, index: number): void {
    if (this.checkForDuplication(event.target.value, index)) {
      return;
    }

    this.statuses[index].loading = true;
    this.nextDisabled = true;
    this.invites.controls[index].controls['merchant'].markAsPending();
    this.userService
      .getUserByReference({
        reference: event.target.value,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.invites.controls[index].controls['merchant'].setErrors(null);
          this.statuses[index].hit = true;
          if (this.selectedMerchants[index]) {
            this.selectedMerchants[index] = res.result.name;
          } else {
            this.selectedMerchants.push(res.result.name);
          }
        } else {
          this.invites.controls[index].controls['merchant'].setErrors({
            incorrect: true,
          });
          this.statuses[index].hit = false;
          if (this.selectedMerchants[index]) {
            this.selectedMerchants[index] = this.errorMessage;
          } else {
            this.selectedMerchants.push(this.errorMessage);
          }
        }

        this.statuses[index].loading = false;
        this.nextDisabled = false;
      });
  }

  saveFormInfo(): void {
    this.packageWizardService.merchants = this.invites.value;
    this.packageWizardService.invitedMerchantsNames = this.selectedMerchants;
  }

  previous(): void {
    this.saveFormInfo();
    this.router.navigate(['/dashboard/package-wizard/add-products']);
  }

  next(): void {
    this.saveFormInfo();
    this.router.navigate(['/dashboard/package-wizard/summary']);
  }
}

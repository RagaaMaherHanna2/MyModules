import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { PackageWizardService } from 'src/app/services/Package/package-wizard.service';
import { PackageService } from 'src/app/services/Package/package.service';
import { environment } from 'src/environments/environment';
import { Product } from 'src/models/Product/models';
import {
  CodeSeparator,
  CodeType,
  CreatePackage,
  inviteMerchantToProduct,
  Package,
  PackageProductLine,
} from 'src/models/package/models';
import { confirmAction } from 'src/store/confirmationSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-package-wizard-summary',
  templateUrl: './package-wizard-summary.component.html',
  styleUrls: ['./package-wizard-summary.component.scss'],
})
export class PackageWizardSummaryComponent implements OnInit {
  package: CreatePackage = {
    code_days_duration: 1,
    code_hours_duration: 0,
    code_separator: CodeSeparator.dash,
    code_type: CodeType.alphanumeric,
    expiry_date: new Date().toISOString(),
    package_name: 'Test Package',
    package_name_ar: 'تجربة',
  };

  merchants: inviteMerchantToProduct[] = [];
  selectedMerchants: string[] = [];

  products: PackageProductLine[] = [];
  selectedProducts: { [key: number]: Product } = {};
  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';

  constructor(
    private packageWizardService: PackageWizardService,
    private router: Router,
    private packageService: PackageService,
    private store: Store
  ) {}

  ngOnInit(): void {
    if (!this.packageWizardService.package) {
      this.router.navigate(['/dashboard/package-wizard/create']);
      return;
    }
    this.package = this.packageWizardService.package;

    if (!this.packageWizardService.products) {
      this.router.navigate(['/dashboard/package-wizard/add-products']);
      return;
    }
    this.products = this.packageWizardService.products;
    this.selectedProducts = this.packageWizardService.selectedProducts;

    if (!this.packageWizardService.merchants) {
      this.router.navigate(['/dashboard/package-wizard/invite-merchants']);
      return;
    }
    this.merchants = this.packageWizardService.merchants;
    this.selectedMerchants = this.packageWizardService.invitedMerchantsNames;
  }

  previous(): void {
    this.router.navigate(['/dashboard/package-wizard/invite-merchants']);
  }

  getProductById(id: number): Product {
    return this.selectedProducts[id];
  }
  getProductSerialsStock(id: number): string {
    return $localize`Product doesn't have vouchers`;
  }

  // TODO:
  // [ ] Fix inviting merchants
  finishWizard(): void {
    this.store.dispatch(
      confirmAction({
        message: $localize`Are your sure you want to create this package?`,
        callbackFunction: () => {
          this.store.dispatch(openLoadingDialog());
          this.packageService.add(this.package).subscribe((res) => {
            if (res.ok) {
              this.packageWizardService.package = {} as Package;
              const reference = res.result.reference;
              this.packageService
                .addVouchers({
                  package: reference,
                  lines: this.products,
                })
                .subscribe((res) => {
                  if (res.ok) {
                    this.packageWizardService.products = [];
                    this.packageWizardService.selectedProducts = [];
                    this.merchants.forEach((merchant) => {
                      merchant.product = reference;
                    });
                    this.packageService
                      .inviteMerchantList({ invites: this.merchants })
                      .subscribe((res) => {
                        if (res.ok) {
                          this.store.dispatch(closeLoadingDialog());
                          this.router.navigate(['dashboard/package/list']);
                        }
                      });
                  }
                });
            }
          });
        },
      })
    );
  }
}

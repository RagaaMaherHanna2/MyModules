import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { PackageWizardService } from 'src/app/services/Package/package-wizard.service';
import { ProductService } from 'src/app/services/Product';
import { environment } from 'src/environments/environment';
import { PackageProductLine } from 'src/models/package/models';
import { Product } from 'src/models/Product/models';

@Component({
  selector: 'app-package-wizard-add-products',
  templateUrl: './package-wizard-add-products.component.html',
  styleUrls: ['./package-wizard-add-products.component.scss'],
})
export class PackageWizardAddProductsComponent
  implements OnInit, AfterViewInit
{
  // TODO:
  // [ ] handle product pagination
  availableProducts: any[] = [];
  selectedProducts: { [key: number]: Product } = {};

  readonly MAX_QUANTITY = environment.MAX_PRODUCT_QUANTITY;
  //BEGIN Product Table Form
  productsForm = this.formBuilder.group({
    products: this.formBuilder.array([]),
  });

  get products() {
    return this.productsForm.controls['products'] as FormArray;
  }
  // END Product Table Form
  constructor(
    private productService: ProductService,
    private formBuilder: FormBuilder,
    private packageWizardService: PackageWizardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (!this.packageWizardService.package) {
      this.router.navigate(['/dashboard/package-wizard/create']);
    }

    this.productService
      .getProductList({
        limit: 20,
        offset: 0,
        name: '',
        category_name: '',
      })
      .subscribe((res) => {
        if (res.ok) {
          this.availableProducts = res.result.data;
        }
        if (this.packageWizardService.products) {
          for (let i = 0; i < this.packageWizardService.products.length; i++) {
            this.addProduct();
          }

          this.productsForm.setValue({
            products: this.packageWizardService.products!,
          });
          this.updateOptionsDisableState();
        } else {
          this.addProduct();
        }
      });
  }
  ngAfterViewInit(): void {}

  addProduct(): void {
    const formRow = this.formBuilder.group({
      product: ['', Validators.required],
      quantity: [0, [Validators.required, Validators.min(1)]],
    });
    this.products.push(formRow);
  }

  updateOptionsDisableState(id: number = -1, removeId: number = -1) {
    const selected: number[] = [];

    if (this.products.value.length > 0) {
      for (let i = 0; i < this.products.value.length; i++) {
        for (let j = 0; j < this.availableProducts.length; j++) {
          if (
            this.availableProducts[j].id === this.products.value[i].product ||
            this.availableProducts[j].id === id
          ) {
            this.availableProducts[j].chosen = true;
            selected.push(this.availableProducts[j].id);
            this.selectedProducts[this.availableProducts[j].id] =
              this.availableProducts[j];
          } else {
            if (
              !selected.find(
                (value) => value === this.availableProducts[j].id
              ) ||
              this.availableProducts[j].id === removeId
            ) {
              this.availableProducts[j].chosen = false;
            }
          }
        }
      }
    } else {
      this.availableProducts.forEach((product) => {
        product.chosen = false;
      });
    }
  }

  getSelectedProductFromId(id: number): Product | null {
    const product =
      this.selectedProducts[this.products.controls[id].value['product']];
    return product ? product : null;
  }

  productHasSerials(id: number): string {
    const product = this.getSelectedProductFromId(id);
    return $localize`Please select a product`;
  }

  productSerialsStock(id: number): string {
    const product = this.getSelectedProductFromId(id);

    if (!product) {
      return $localize`Please select a product`;
    }

    return $localize`Product do not have vouchers`;
  }

  saveFormInfo(): void {
    this.packageWizardService.products = this.products.value;
    this.packageWizardService.selectedProducts = this.selectedProducts;
  }

  deleteProduct(productIndex: number): void {
    this.products.removeAt(productIndex);
    this.updateOptionsDisableState(-1, productIndex);
  }

  previous(): void {
    this.saveFormInfo();
    this.router.navigate(['dashboard/package-wizard/create']);
  }

  next(): void {
    this.saveFormInfo();
    this.router.navigate(['/dashboard/package-wizard/invite-merchants']);
  }
}

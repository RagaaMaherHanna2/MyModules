import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { PackageService } from 'src/app/services/Package/package.service';
import { ProductService } from 'src/app/services/Product';
import { Product } from 'src/models/Product/models';
import { Package, PackageProductLine } from 'src/models/package/models';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-add-vouchers',
  templateUrl: './add-vouchers.component.html',
  styleUrls: ['./add-vouchers.component.scss'],
})
export class AddVouchersComponent implements OnInit {
  package: Package = {} as Package;
  locale = $localize.locale;
  availableProducts: any[] = [];

  // Product Table Form
  productsForm = this.formBuilder.group({
    products: this.formBuilder.array([]),
  });

  get products() {
    return this.productsForm.controls['products'] as FormArray;
  }
  // END Product Table Form
  constructor(
    private packageService: PackageService,
    private activatedRout: ActivatedRoute,
    private productService: ProductService,
    private formBuilder: FormBuilder,
    private store: Store,
    private messageService: MessageService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.activatedRout.params.subscribe((params) => {
      const packageReference: string = params['reference'];
      this.packageService
        .details({ reference: packageReference })
        .subscribe((res) => {
          if (res.ok) {
            this.package = res.result.data[0];
          }
        });
    });
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
      });
    this.addProduct();
  }

  addProduct(): void {
    const formRow = this.formBuilder.group({
      product: ['', Validators.required],
      quantity: [0, [Validators.required, Validators.min(1)]],
    });

    this.products.push(formRow);
  }

  deleteProduct(productIndex: number): void {
    this.products.removeAt(productIndex);
  }

  onDropdownChange(event: any): void {
    this.availableProducts.forEach((product) => {
      if (product.id === event.value) {
        product.chosen = true;
      }
    });
  }

  onSubmit(event: SubmitEvent): void {
    this.store.dispatch(openLoadingDialog());
    const lines: PackageProductLine[] = [];
    this.products.controls.forEach((line) => {
      lines.push({
        product: line.value.product,
        quantity: line.value.quantity,
      });
    });
    this.packageService
      .addVouchers({
        package: this.package.reference!,
        lines,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.store.dispatch(closeLoadingDialog());
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: res.message,
          });
          this.router.navigate([
            '/dashboard/package/details',
            this.package.reference,
          ]);
        }
      });
  }
}

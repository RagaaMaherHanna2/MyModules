import { Injectable } from '@angular/core';
import { Product } from 'src/models/Product/models';
import { inviteMerchantToProduct } from 'src/models/package/models';
import { PackageProductLine } from 'src/models/package/models';
import { CreatePackage } from 'src/models/package/models';

@Injectable({
  providedIn: 'any',
})
export class PackageWizardService {
  package: CreatePackage;

  products: PackageProductLine[];
  selectedProducts: { [key: number]: Product };

  merchants: inviteMerchantToProduct[];
  invitedMerchantsNames: string[];

  constructor() {}
}

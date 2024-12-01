import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MenuItem, MessageService } from 'primeng/api';
import { RedeemService } from 'src/app/services/redeem/redeem.service';
import { ProductAttribute } from 'src/models/Product/models';
import { SPdata, ServiceProviderProfile } from 'src/models/User';

@Component({
  selector: 'app-redeem-page',
  templateUrl: './redeem-page.component.html',
  styleUrls: ['./redeem-page.component.scss'],
})
export class RedeemPageComponent {
  stepsModel: any[];
  activeIndex: number = 0;
  SPdetails: SPdata;
  dynamicAttributes: ProductAttribute[];

  constructor(
    private activatedRoute: ActivatedRoute,
    private redeemService: RedeemService,
    private router: Router
  ) {}

  onActiveIndexChange(event: number) {
    this.activeIndex = event;
  }

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      const redirectToFirstStep = sessionStorage.getItem('redirectToFirstStep');
      if (redirectToFirstStep) {
        sessionStorage.removeItem('redirectToFirstStep');
        this.router.navigate([
          `redeem-page/${params['sp-hash']}/${params['product_sku']}`,
        ]);
      }
      this.redeemService
        .authServiceProviderWithHash(params['sp-hash'], params['product_sku'])
        .subscribe((res) => {
          if (res.ok) {
            this.SPdetails = res.result.user;
            this.dynamicAttributes = res.result.product_attributes[0];
          }
        });
    });
    this.stepsModel = [
      {
        routerLink: '',
        label: 'Check Code',
      },
      {
        routerLink: 'redeem-code',
        label: 'Redeem Code',
      },
    ];
  }
}

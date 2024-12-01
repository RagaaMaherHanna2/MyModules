import { CommonModule } from '@angular/common';
import { OnInit, ElementRef } from '@angular/core';
import { Component } from '@angular/core';
import { LayoutService } from 'src/app/services/layout.service';
import { SidebarItemComponent } from './sidebar-item/sidebar-item.component';
import { Store, createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { MenuItem } from 'primeng/api';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import { setAccessRights, setUser } from 'src/store/accessRightSlice';
import { PermissionService } from 'src/app/services/permission/permission.service';

@Component({
  selector: 'layout-sidebar',
  templateUrl: './sidebar.component.html',
  imports: [CommonModule, SidebarItemComponent],
  standalone: true,
})
export class SidebarComponent implements OnInit {
  model: MenuItem[] = [];
  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state)
  );
  serviceProviderModel: MenuItem[] = [
    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Home`,
          icon: 'pi pi-home',
          routerLink: ['/dashboard'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Categories`,
          icon: 'pi pi-tag',
          items: [
            {
              label: $localize`Create Category`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/category/create'],
            },
            {
              label: $localize`Categories List`,
              icon: 'pi pi-tags',
              routerLink: ['/dashboard/category/list'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Products`,
          icon: 'pi pi-tag',
          items: [
            {
              label: $localize`Create Product`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/product/create-product'],
            },
            {
              label: $localize`Products List`,
              icon: 'pi pi-tags',
              routerLink: ['/dashboard/product/list'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Vendors`,
          icon: 'pi pi-users',
          routerLink: ['/dashboard/vendors/list'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Reports`,
          icon: 'pi pi-file-o',
          items: [
            {
              label: $localize`Create Sales Report`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/reports/create-sale-report'],
            },
            {
              label: $localize`Sales Reports`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/reports/list-sales-reports'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Codes`,
          icon: 'pi pi-ticket',
          items: [
            {
              label: $localize`Check Codes`,
              icon: 'pi pi-check-circle',
              routerLink: ['/dashboard/code/check'],
            },
            {
              label: $localize`Check Prepaid Balance`,
              icon: 'pi pi-money-bill',
              routerLink: ['/dashboard/prepaid/check-balance'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Redeem History`,
          icon: 'pi pi-align-center',
          routerLink: ['/dashboard/redeem-history'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Vouchers Batches`,
          icon: 'pi pi-align-justify',
          routerLink: ['/dashboard/serials-batches/list'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Merchants`,
          icon: 'pi pi-users',
          routerLink: ['/dashboard/merchants'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Taxes`,
          icon: 'pi pi-percentage',
          items: [
            {
              label: $localize`Create Tax`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/taxes/create-tax'],
            },
            {
              label: $localize`Taxes Table`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/taxes/list-taxes'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Invoices`,
          icon: 'pi pi-money-bill',
          items: [
            {
              label: $localize`Create Invoice`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/invoices/create'],
            },
            {
              label: $localize`Merchants Invoice Table`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/invoices/list'],
            },
            {
              label: $localize`Bills`,
              icon: 'pi pi-credit-card',
              routerLink: ['/dashboard/invoices/bills'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Wallet Management`,
          icon: 'pi pi-wallet',
          items: [
            // {
            //   label: $localize`LikeCard Vouchers`,
            //   icon: 'pi pi-dollar',
            //   routerLink: ['/dashboard/wallet/redeem-balance-voucher'],
            // },
            // {
            //   label: $localize`Submit Bank Transfer`,
            //   icon: 'pi pi-pound',
            //   routerLink: ['/dashboard/wallet/add-charge-request'],
            // },
            // {
            //   label: $localize`Request Credit`,
            //   icon: 'pi pi-money-bill',
            //   routerLink: ['/dashboard/wallet/add-credit-request'],
            // },
            // {
            //   label: $localize`Bank Transfer Requests`,
            //   icon: 'pi pi-list',
            //   routerLink: ['/dashboard/wallet/view-charge-request'],
            // },
            {
              label: $localize`Merchant Credit Requests`,
              icon: 'pi pi-list',
              routerLink: ['/dashboard/wallet/view-credit-request'],
            },
            {
              label: $localize`Banks`,
              icon: 'pi pi-building',
              routerLink: ['/dashboard/wallet/bank-list'],
            },
          ],
        },
      ],
    },

    {
      label: '',
      items: [
        {
          label: $localize`Settings`,
          icon: 'pi pi-cog',
          items: [
            {
              label: $localize`API Keys Management`,
              icon: 'pi pi-code',
              routerLink: ['/dashboard/settings/api-keys-management'],
            },

            {
              label: $localize`Notifications`,
              icon: 'pi pi-bell',
              routerLink: ['/dashboard/settings/notifications'],
            },
            {
              label: $localize`Two Factor Authentication`,
              icon: 'pi pi-lock',
              routerLink: ['/dashboard/settings/Two-Factor-Authentication'],
            },
            {
              label: $localize`Change Password`,
              icon: 'pi pi-ellipsis-h',
              routerLink: ['/auth/change-password'],
            },
          ],
        },
      ],
    },
  ];

  merchantModel: MenuItem[] = [
    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Home`,
          icon: 'pi pi-chart-bar',
          routerLink: ['/dashboard'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Products`,
          icon: 'pi pi-tags',
          routerLink: ['/dashboard/merchant/product/list'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Reports`,
          icon: 'pi pi-file-o',
          items: [
            {
              label: $localize`Create Sales Report`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/reports/create-sale-report'],
            },
            {
              label: $localize`Sales Reports Table`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/reports/list-sales-reports'],
            },
          ],
        },
      ],
    },
    // {
    //   label: '',
    //   items: [
    //     {
    //       label: $localize`Package`,
    //       items: [
    //         {
    //           label: $localize`Available Packages`,
    //           icon: 'pi pi-folder-open',
    //           routerLink: ['/dashboard/merchant/package/list'],
    //         },
    //       ],
    //     },
    //   ],
    // },

    {
      label: '',
      items: [
        {
          label: $localize`Orders`,
          icon: 'pi pi-check-circle',
          routerLink: ['/dashboard/orders'],
        },
      ],
    },

    {
      label: '',
      items: [
        {
          label: $localize`Check Prepaid Balance`,
          icon: 'pi pi-money-bill',
          routerLink: ['/dashboard/prepaid/check-balance'],
        },
      ],
    },

    {
      label: '',
      items: [
        {
          label: $localize`Invoices`,
          icon: 'pi pi-money-bill',
          items: [
            {
              label: $localize`Invoices Table`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/invoices/list'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Sub Merchants`,
          icon: 'pi pi-users',
          routerLink: ['/dashboard/sub-merchants/list'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Wallet Management`,
          icon: 'pi pi-wallet',
          items: [
            /*
            {
              label: $localize`LikeCard Vouchers`,
              icon: 'pi pi-dollar',
              routerLink: ['/dashboard/wallet/redeem-balance-voucher'],
            },
  */ {
              label: $localize`Submit Bank Transfer`,
              icon: 'pi pi-pound',
              routerLink: ['/dashboard/wallet/add-charge-request'],
            },
            {
              label: $localize`Bank Transfer Requests`,
              icon: 'pi pi-list',
              routerLink: ['/dashboard/wallet/view-charge-request'],
            },
            {
              label: $localize`Banks`,
              icon: 'pi pi-building',
              routerLink: ['/dashboard/wallet/bank-list'],
            },
          ],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Settings`,
          icon: 'pi pi-cog',
          routerLink: ['/dashboard/settings/account'],
          items: [
            {
              label: $localize`Account Settings`,
              icon: 'pi pi-user',
              routerLink: ['/dashboard/settings/account'],
            },
            {
              label: $localize`Change Password`,
              icon: 'pi pi-ellipsis-h',
              routerLink: ['/auth/change-password'],
            },
            {
              label: $localize`Notifications`,
              icon: 'pi pi-bell',
              routerLink: ['/dashboard/settings/notifications'],
            },
            {
              label: $localize`Two Factor Authentication`,
              icon: 'pi pi-lock',
              routerLink: ['/dashboard/settings/Two-Factor-Authentication'],
            },
          ],
        },
      ],
    },
  ];
  subMerchantModel: MenuItem[];
  accountManagerModel: MenuItem[] = [
    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Home`,
          icon: 'pi pi-home',
          routerLink: ['/dashboard'],
        },
      ],
    },
    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Reports`,
          icon: 'pi pi-file-o',
          items: [
            {
              label: $localize`Create Fees Report`,
              icon: 'pi pi-plus',
              routerLink: ['/dashboard/reports/create-fees-report'],
            },
            {
              label: $localize`Fees Reports`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/reports/fees-reports'],
            },
            {
              label: $localize`Daily Fees Reports`,
              icon: 'pi pi-align-center',
              routerLink: ['/dashboard/reports/daily-fees-reports'],
            },
          ],
        },
      ],
    },
  ];
  spFinanceModel: MenuItem[] = [
    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Home`,
          icon: 'pi pi-home',
          routerLink: ['/dashboard'],
        },
      ],
    },
    {
      label: '',
      items: [
        {
          label: $localize`Products List`,
          icon: 'pi pi-tags',
          routerLink: ['/dashboard/product/list'],
        },
      ],
    },

    {
      // First label is empty to make menu collapsable.
      label: '',
      items: [
        {
          label: $localize`Reports`,
          icon: 'pi pi-file-o',
          items: [
            {
              label: $localize`Voucher Batches Report`,
              icon: 'pi pi-briefcase',
              routerLink: ['/dashboard/reports/batches-report'],
            },
          ],
        },
      ],
    },
  ];
  constructor(
    public layoutService: LayoutService,
    public el: ElementRef,
    private store: Store,
    private authService: AuthService,
    private permissionService: PermissionService
  ) {}

  ngOnInit() {
    this.authService.whoAmI().subscribe((res) => {
      if (res.ok) {
        localStorage.setItem(
          environment.USER_ROLES_KEY,
          JSON.stringify(res.result.roles)
        );
        localStorage.setItem(environment.USER_KEY, JSON.stringify(res.result));
        localStorage.setItem(environment.BALANCE_KEY, '0');
        localStorage.setItem(
          environment.CODES_ADDITIONAL_VALUE,
          res.result.codes_additional_value
        );

        this.store.dispatch(setAccessRights({ role: res.result.roles }));
        this.store.dispatch(setUser({ user: res.result }));
      }
    });
    this.accessRole$.subscribe((state) => {
      this.model = [];
      if (state.role.includes('service_provider')) {
        this.model = [...this.model, ...this.serviceProviderModel];
      }
      if (state.role.includes('merchant')) {
        this.model = [...this.model, ...this.merchantModel];
      }
      if (state.role.includes('submerchant')) {
        this.initSubMerchantModel();
        console.log(1, this.subMerchantModel);
        this.model = [...this.model, ...this.subMerchantModel];
        console.log(2, this.model);
      }

      if (state.role.includes('accountant Manager')) {
        this.model = [...this.model, ...this.accountManagerModel];
      }
      if (state.role.includes('sp_finance')) {
        this.model = [...this.model, ...this.spFinanceModel];
      }
    });
  }
  checkPermission(code: string): boolean {
    console.log(this.permissionService.checkUserPermission(code));
    return this.permissionService.checkUserPermission(code);
  }
  checkCategory(category: string): boolean {
    return this.permissionService.checkUserPermissionCategory(category);
  }
  initSubMerchantModel() {
    this.subMerchantModel = [
      {
        // First label is empty to make menu collapsable.
        label: '',
        items: [
          {
            label: $localize`Home`,
            icon: 'pi pi-chart-bar',
            routerLink: ['/dashboard'],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('products'),
        items: [
          {
            label: $localize`Products`,
            visible: this.checkPermission('1.1'),
            icon: 'pi pi-tags',
            routerLink: ['/dashboard/merchant/product/list'],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('reports'),
        items: [
          {
            label: $localize`Reports`,
            icon: 'pi pi-file-o',
            items: [
              {
                label: $localize`Create Sales Report`,
                visible: this.checkPermission('2.1'),
                icon: 'pi pi-plus',
                routerLink: ['/dashboard/reports/create-sale-report'],
              },
              {
                label: $localize`Sales Reports Table`,
                visible: this.checkPermission('2.2'),
                icon: 'pi pi-briefcase',
                routerLink: ['/dashboard/reports/list-sales-reports'],
              },
            ],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('orders'),
        items: [
          {
            label: $localize`Orders`,
            icon: 'pi pi-check-circle',
            routerLink: ['/dashboard/orders'],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('codes'),
        items: [
          {
            label: $localize`Check Prepaid Balance`,
            icon: 'pi pi-money-bill',
            routerLink: ['/dashboard/prepaid/check-balance'],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('invoices'),
        items: [
          {
            label: $localize`Invoices`,
            icon: 'pi pi-money-bill',
            items: [
              {
                label: $localize`Invoices Table`,
                visible: this.checkPermission('5'),
                icon: 'pi pi-briefcase',
                routerLink: ['/dashboard/invoices/list'],
              },
            ],
          },
        ],
      },
      {
        label: '',
        visible: this.checkCategory('wallet'),
        items: [
          {
            label: $localize`Wallet Management`,
            icon: 'pi pi-wallet',
            items: [
              {
                label: $localize`Submit Bank Transfer`,
                visible: true,
                icon: 'pi pi-pound',
                routerLink: ['/dashboard/wallet/add-charge-request'],
              },
              {
                label: $localize`Bank Transfer Requests`,
                visible: true,
                icon: 'pi pi-list',
                routerLink: ['/dashboard/wallet/view-charge-request'],
              },
              {
                label: $localize`Banks`,
                visible: true,
                icon: 'pi pi-building',
                routerLink: ['/dashboard/wallet/bank-list'],
              },
            ],
          },
        ],
      },
      {
        label: '',
        items: [
          {
            label: $localize`Settings`,
            icon: 'pi pi-cog',
            routerLink: ['/dashboard/settings/account'],
            items: [
              {
                label: $localize`Account Settings`,
                icon: 'pi pi-user',
                routerLink: ['/dashboard/settings/account'],
              },
              {
                label: $localize`Change Password`,
                icon: 'pi pi-ellipsis-h',
                routerLink: ['/auth/change-password'],
              },
              {
                label: $localize`Notifications`,
                icon: 'pi pi-bell',
                routerLink: ['/dashboard/settings/notifications'],
              },
              {
                label: $localize`Two Factor Authentication`,
                icon: 'pi pi-lock',
                routerLink: ['/dashboard/settings/Two-Factor-Authentication'],
              },
            ],
          },
        ],
      },
    ];
  }
}

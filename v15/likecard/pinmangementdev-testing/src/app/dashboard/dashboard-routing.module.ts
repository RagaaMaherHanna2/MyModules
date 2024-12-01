import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { StatisticsComponent } from './statistics/statistics/statistics.component';

const routes: Routes = [
  {
    path: '',
    component: DashboardComponent,
    children: [
      {
        path: '',
        loadChildren: () =>
          import('./statistics/statistics.module').then(
            (m) => m.StatisticsModule
          ),
      },
      {
        path: 'wallet',
        loadChildren: () =>
          import('./wallet/wallet.module').then((m) => m.WalletModule),
      },
      {
        path: 'product',
        loadChildren: () =>
          import('./products/products.module').then((m) => m.ProductsModule),
      },
      {
        path: 'category',
        loadChildren: () =>
          import('./categories/categories.module').then(
            (m) => m.CategoriesModule
          ),
      },
      {
        path: 'reports',
        loadChildren: () =>
          import('./reports/reports.module').then((m) => m.ReportsModule),
      },
      {
        path: 'taxes',
        loadChildren: () =>
          import('./taxes/taxes.module').then((m) => m.TaxesModule),
      },
      {
        path: 'package',
        loadChildren: () =>
          import('./package/package.module').then((m) => m.PackageModule),
      },
      {
        path: 'package-wizard',
        loadChildren: () =>
          import('./package-wizard/package-wizard.module').then(
            (m) => m.PackageWizardModule
          ),
      },
      {
        path: 'orders',
        loadChildren: () =>
          import('./orders/orders.module').then((m) => m.OrdersModule),
      },
      {
        path: 'settings',
        loadChildren: () =>
          import('./layout/settings/settings.module').then(
            (m) => m.SettingsModule
          ),
      },
      {
        path: 'merchant',
        loadChildren: () =>
          import('./merchant-dashboard/merchant-dashboard.module').then(
            (m) => m.MerchantDashboardModule
          ),
      },
      {
        path: 'sub-merchants',
        loadChildren: () =>
          import('./sub-merchants/sub-merchants.module').then(
            (m) => m.SubMerchantsModule
          ),
      },
      {
        path: 'redeem-history',
        loadChildren: () =>
          import('./redeem-history/redeem-history.module').then(
            (m) => m.RedeemHistoryModule
          ),
      },
      {
        path: 'balance',
        loadChildren: () =>
          import('./balance/balance.module').then((m) => m.BalancModule),
      },
      {
        path: 'code',
        loadChildren: () =>
          import('./codes/codes.module').then((m) => m.CodesModule),
      },
      {
        path: 'merchants',
        loadChildren: () =>
          import('./merchants/merchants.module').then((m) => m.MerchantsModule),
      },
      {
        path: 'prepaid',
        loadChildren: () =>
          import('./prepaid/prepaid.module').then((m) => m.PrepaidModule),
      },
      {
        path: 'serials-batches',
        loadChildren: () =>
          import('./serials-batches/serials-batches.module').then(
            (m) => m.SerialsBatchesModule
          ),
      },
      {
        path: 'invoices',
        loadChildren: () =>
          import('./invoices/invoices.module').then((m) => m.InvoicesModule),
      },
      {
        path: 'vendors',
        loadChildren: () =>
          import('./vendors/vendors.module').then((m) => m.VendorsModule),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'home',
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class DashboardRoutingModule {}

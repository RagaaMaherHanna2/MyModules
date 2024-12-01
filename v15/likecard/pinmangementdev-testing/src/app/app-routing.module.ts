import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { GuestGuard } from './guards/guest.guard';

const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'dashboard',
    canMatch: [AuthGuard],
  },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./dashboard/dashboard.module').then((m) => m.DashboardModule),
    canMatch: [AuthGuard],
  },
  {
    path: 'auth',
    loadChildren: () =>
      import('./dashboard/auth/auth.module').then((m) => m.AuthModule),
  },
  {
    path: 'redeem-page',
    loadChildren: () =>
      import('./dashboard/redeem-page/redeem-page.module').then(
        (m) => m.RedeemPageModule
      ),
  },
  {
    path: 'foodics',
    loadChildren: () =>
      import('./dashboard/foodics/foodics.module').then((m) => m.FoodicsModule),
  },
  {
    path: 'foodics-success',
    loadChildren: () =>
      import('./dashboard/foodics-success/foodics-success.module').then(
        (m) => m.FoodicsSuccessModule
      ),
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

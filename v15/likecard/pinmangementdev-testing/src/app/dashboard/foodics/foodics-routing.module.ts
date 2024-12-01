import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FoodicsLoginComponent } from './foodics-login/foodics-login.component';
import { FoodicsConnectComponent } from './foodics-connect/foodics-connect.component';
import { FoodicsGuard } from 'src/app/guards/foodics.guard';
import { FoodicsNewComponent } from '../foodics-success/foodics-new/foodics-new.component';

const routes: Routes = [
  {
    path: '',
    children: [
      {
        path: 'login',
        component: FoodicsLoginComponent,
      },
      {
        path: 'connect',
        component: FoodicsConnectComponent,
        canMatch: [FoodicsGuard],
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class FoodicsRoutingModule {}

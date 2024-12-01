import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OrdersComponent } from './list-orders/orders.component';
import { OrdersDetailsComponent } from './orders-details/orders-details.component';


const routes: Routes = [
  {
    path: '',
    component: OrdersComponent,
  },
  { path: 'details/:id', component: OrdersDetailsComponent },]

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrdersRoutingModule { }

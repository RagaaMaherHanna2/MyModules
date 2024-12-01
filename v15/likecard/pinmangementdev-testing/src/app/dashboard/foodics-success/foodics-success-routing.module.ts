import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FoodicsNewComponent } from './foodics-new/foodics-new.component';

const routes: Routes = [
  {
    path: '',
    component: FoodicsNewComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class FoodicsSuccessRoutingModule {}

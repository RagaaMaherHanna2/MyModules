import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { FoodicsRoutingModule } from './foodics-routing.module';
import { FoodicsLoginComponent } from './foodics-login/foodics-login.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from 'primeng/api';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { NgOtpInputModule } from 'ng-otp-input';
import { FoodicsConnectComponent } from './foodics-connect/foodics-connect.component';
import { FoodicsNewComponent } from '../foodics-success/foodics-new/foodics-new.component';
import { DialogModule } from 'primeng/dialog';

@NgModule({
  declarations: [
    FoodicsLoginComponent,
    FoodicsConnectComponent,
    FoodicsNewComponent,
  ],
  imports: [
    CommonModule,
    FoodicsRoutingModule,
    ReactiveFormsModule,
    SharedModule,
    PasswordModule,
    InputTextModule,
    ButtonModule,
    NgOtpInputModule,
    DialogModule,
  ],
})
export class FoodicsModule {}

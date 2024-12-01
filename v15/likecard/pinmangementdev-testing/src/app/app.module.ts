import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule, isDevMode } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { StoreModule } from '@ngrx/store';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

// Store Slices
import loadingReducer, {
  name as LoadingFeatureKey,
} from 'src/store/loadingSlice';
import confirmationReducer, {
  name as ConfirmationFeatureKey,
} from 'src/store/confirmationSlice';
import errorReducer, { name as ErrorFeatureKey } from 'src/store/errorSlice';
import accessRightReducer, {
  name as AccessRightFeatureKey,
} from 'src/store/accessRightSlice';
import balanceReducer, {
  name as BalanceFeatureKey,
} from 'src/store/balanceSlice';
// END Store Slices

import { SharedModule } from './shared/shared.module';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { ErrorInterceptor } from './interceptors/error.interceptor';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    StoreModule.forRoot({}, {}),
    StoreModule.forFeature(LoadingFeatureKey, loadingReducer),
    StoreModule.forFeature(ConfirmationFeatureKey, confirmationReducer),
    StoreModule.forFeature(ErrorFeatureKey, errorReducer),
    StoreModule.forFeature(AccessRightFeatureKey, accessRightReducer),
    StoreModule.forFeature(BalanceFeatureKey, balanceReducer),
    StoreDevtoolsModule.instrument({ maxAge: 25, logOnly: !isDevMode() }),
    SharedModule,
    ToastModule,
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorInterceptor,
      multi: true,
    },
    MessageService,
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}

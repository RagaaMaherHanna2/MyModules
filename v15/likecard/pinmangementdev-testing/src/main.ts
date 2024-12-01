/// <reference types="@angular/localize" />
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';

import { environment } from 'src/environments/environment';
export function getBaseUrl() {
  return environment.API_URL;
}
const providers = [{ provide: 'BASE_URL', useFactory: getBaseUrl, deps: [] }];

platformBrowserDynamic(providers)
  .bootstrapModule(AppModule)
  .catch((err) => console.error(err));

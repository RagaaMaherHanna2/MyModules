// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
export const environment = {
  production: false,
  staging: false,
  vendor: false,
  TOKEN_KEY: 'redeemly_partner_token',
  PAGE_SIZE: 10,
  MAX_UPLOADED_FILE_SIZE: 1000000,
  // API_URL: 'http://15.184.127.72:8073/',
  API_URL: 'http://localhost:8010',
  EXCEL_FILE_TYPES:
    '.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel',
  IMAGE_FILE_TYPES: 'image/*',
  USER_ROLES_KEY: 'dashboard_user_roles',
  USER_KEY: 'dashboard_user',
  BALANCE_KEY: 'user_balance',
  MAX_PRODUCT_QUANTITY: 50000,
  URL_PATTERN: '(http(s)?://)?([\\da-z.-]+)\\.([a-z.]{2,6})[/\\w .-]*/?',
  DASHBOARD_LINK: 'http://localhost:4200',
  KEY: 'key',
  LOGIN_EMAIL: 'login_email',
  CURRENCY_SYMBOL: 'currency_symbol',
  CODES_ADDITIONAL_VALUE: 'codes_additional_value',
  FOODICS_STATE: 'foodics_state',
  FOODICS_CLIENT_ID: 'foodics_client_id',
  COUNTRIES: 'countries',
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.

export const environment = {
  production: true,
  preprod: false,
  staging: false,
  vendor: false,
  TOKEN_KEY: 'redeemly_partner_token',
  PAGE_SIZE: 20,
  MAX_UPLOADED_FILE_SIZE: 1000000,
  API_URL: 'https://onlineapi.skarla.com',
  EXCEL_FILE_TYPES:
    '.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel',
  IMAGE_FILE_TYPES: 'image/*',
  USER_ROLES_KEY: 'dashboard_user_roles',
  USER_KEY: 'dashboard_user',
  BALANCE_KEY: 'user_balance',
  MAX_PRODUCT_QUANTITY: 50000,
  URL_PATTERN: '(http(s)?://)?([\\da-z.-]+)\\.([a-z.]{2,6})[/\\w .-]*/?',
  DASHBOARD_LINK: 'https://portal.skarla.com',
  KEY: 'key',
  LOGIN_EMAIL: 'login_email',
  CODES_ADDITIONAL_VALUE: 'codes_additional_value',
  CURRENCY_SYMBOL: 'currency_symbol',
  FOODICS_STATE: 'foodics_state',
  FOODICS_CLIENT_ID: 'foodics_client_id',
  COUNTRIES: 'countries',
};

export type FoodicsLoginBody = {
  login: string;
  password: string;
};
export type FoodicsLoginResponse = {
  token: string;
  is_2factor: boolean;
};

export type FoodicsPreinstallResponse = {
  redirect_url: string;
};

export type FoodicsNewBody = {
  code: string;
  state: string;
};

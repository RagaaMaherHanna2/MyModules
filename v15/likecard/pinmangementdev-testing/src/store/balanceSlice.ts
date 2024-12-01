import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createFeatureSelector } from '@ngrx/store';

interface BalanceState {
  balance: number;
  currency: string;
}

const initialState: BalanceState = {
  balance: 0,
  currency: 'USD',
};

const balanceSlice = createSlice({
  name: 'balance',
  initialState,
  reducers: {
    setBalance: (state, action: PayloadAction<BalanceState>) => {
      state.balance = action.payload.balance;
      state.currency = action.payload.currency;
    },
  },
});

export const { setBalance } = balanceSlice.actions;
export const { name } = balanceSlice;
export const balanceFeature =
  createFeatureSelector<ReturnType<typeof balanceSlice.reducer>>(name);
export default balanceSlice.reducer;

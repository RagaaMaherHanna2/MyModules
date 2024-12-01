import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createFeatureSelector } from '@ngrx/store';

interface errorState {
  open: boolean;
  message: string;
  logout?: Boolean;
}

const initialState: errorState = {
  open: false,
  message: $localize`An error happened. Please try again`,
  logout: false,
};

const errorSlice = createSlice({
  name: 'error',
  initialState,
  reducers: {
    openErrorDialog: (
      state,
      action: PayloadAction<{ message?: string; logout?: boolean }>
    ) => {
      state.open = true;
      state.logout = action.payload.logout ?? false;
      state.message = action.payload.message ?? initialState.message;
    },
    closeErrorDialog: (state) => {
      state.open = false;
    },
  },
});

export const { closeErrorDialog, openErrorDialog } = errorSlice.actions;
export const { name } = errorSlice;
export const errorFeature =
  createFeatureSelector<ReturnType<typeof errorSlice.reducer>>(name);
export default errorSlice.reducer;

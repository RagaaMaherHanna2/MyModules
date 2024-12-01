import { createSlice } from '@reduxjs/toolkit';
import { createFeatureSelector } from '@ngrx/store';

interface LoadingState {
  open: boolean;
}
const loadingSlice = createSlice({
  name: 'loading',
  initialState: {
    open: false,
  },
  reducers: {
    openLoadingDialog: (state: LoadingState) => {
      state.open = true;
    },
    closeLoadingDialog: (state: LoadingState) => {
      state.open = false;
    },
  },
});

export const { closeLoadingDialog, openLoadingDialog } = loadingSlice.actions;
export const { name } = loadingSlice;

export const loadingFeature =
  createFeatureSelector<ReturnType<typeof loadingSlice.reducer>>(name);
export default loadingSlice.reducer;


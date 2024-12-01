import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createFeatureSelector } from '@ngrx/store';

interface ConfirmationState {
  message: string;

  callbackFunction: () => void;
  icon: string;
  open: boolean;
}
interface ConfirmActionContext {
  message?: string;
  callbackFunction: () => void;
  icon?: string;
}
const initialState: ConfirmationState = {
  message: $localize`Are you sure you want to perform this action?`,
  callbackFunction: () => {},
  icon: 'pi pi-exclamation-triangle',
  open: false,
};
const confirmationSlice = createSlice({
  name: 'confirmation',
  initialState,

  reducers: {
    confirmAction: (state, action: PayloadAction<ConfirmActionContext>) => {
      state.open = true;
      state.message = action.payload.message ?? initialState.message;
      state.icon = action.payload.icon ?? initialState.icon;
      state.callbackFunction = action.payload.callbackFunction;
    },
    closeConfirmationDialog: (state) => {
      state.open = false;
    },
  },
});

export const { closeConfirmationDialog, confirmAction } =
  confirmationSlice.actions;
export const { name } = confirmationSlice;
export const confirmationFeature =
  createFeatureSelector<ReturnType<typeof confirmationSlice.reducer>>(name);
export default confirmationSlice.reducer;

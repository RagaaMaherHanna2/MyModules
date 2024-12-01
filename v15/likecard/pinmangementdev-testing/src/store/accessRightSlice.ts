import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createFeatureSelector } from '@ngrx/store';
import { environment } from 'src/environments/environment';
import { DashboardUser } from 'src/models/User';

interface AccessRoleState {
  [x: string]: any;
  role: string[];
  user: DashboardUser;
  permissions: any[];
}

const initialState: AccessRoleState = {
  role: JSON.parse(localStorage.getItem(environment.USER_ROLES_KEY) ?? '[]'),
  user: JSON.parse(localStorage.getItem(environment.USER_KEY) ?? '{}'),
  permissions: [],
};

const accessRightSlice = createSlice({
  name: 'access',
  initialState,
  reducers: {
    setAccessRights: (state, action: PayloadAction<{ role: string[] }>) => {
      state.role = action.payload.role;
    },
    setUser: (state, action: PayloadAction<{ user: DashboardUser }>) => {
      state.user = action.payload.user;
    },
  },
});

export const { setAccessRights, setUser } = accessRightSlice.actions;
export const { name } = accessRightSlice;
export const accessRightFeature =
  createFeatureSelector<ReturnType<typeof accessRightSlice.reducer>>(name);
export default accessRightSlice.reducer;

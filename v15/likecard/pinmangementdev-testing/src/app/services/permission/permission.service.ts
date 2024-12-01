import { Injectable } from '@angular/core';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { Store, createSelector } from '@ngrx/store';
import { state } from '@angular/animations';

interface Permission {
  id: string;
  isEnabled: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class PermissionService {
  constructor(private store: Store) {}

  Permissions: any[] = [];
  userRole: string[];

  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state)
  );

  checkUserPermission(permissionCode: string): boolean {
    this.accessRole$.subscribe((state) => {
      this.Permissions = state.user.permissions;
      console.log(this.Permissions);
      this.userRole = state.user.roles;
    });

    const hasPermission: boolean = !!this.Permissions.find(
      (permission) => permission.code === permissionCode
    );
    return this.userRole[0] === 'submerchant' ? hasPermission : true;
  }
  checkUserPermissionCategory(category: string): boolean {
    this.accessRole$.subscribe((state) => {
      this.Permissions = state.user.permissions;
    });
    const hasCategoryPermission: boolean = !!this.Permissions.find(
      (permission) =>
        permission.category === category && ![26, 27].includes(permission.id)
    );
    return hasCategoryPermission;
  }
}

import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  CanActivate,
  CanMatch,
  Route,
  Router,
  RouterStateSnapshot,
  UrlSegment,
  UrlTree,
} from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ChangePasswordGuard implements CanMatch {
  constructor(private router: Router) {}
  canMatch(
    route: Route,
    segments: UrlSegment[]
  ):
    | Observable<boolean | UrlTree>
    | Promise<boolean | UrlTree>
    | boolean
    | UrlTree {
    const loginEmail = localStorage.getItem(environment.LOGIN_EMAIL);
    const token = localStorage.getItem(environment.TOKEN_KEY);
    if (loginEmail && token) {
      return true;
    } else {
      localStorage.clear();
      return this.router.parseUrl('/auth/login');
    }
  }
}

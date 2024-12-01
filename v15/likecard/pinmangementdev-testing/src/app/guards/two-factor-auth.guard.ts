import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanMatch, Route, Router, RouterStateSnapshot, UrlSegment, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TwoFactorAuthGuard implements CanMatch {
  constructor(private router: Router) { }
  canMatch(
    route: Route,
    segments: UrlSegment[]
  ):
    | Observable<boolean | UrlTree>
    | Promise<boolean | UrlTree>
    | boolean
    | UrlTree {
      let first_login= JSON.parse(localStorage.getItem('first_login') || '{}')
     
    if (localStorage.getItem(environment.LOGIN_EMAIL) && localStorage.getItem(environment.KEY) ) {
      return true;
    }
    else{
      return this.router.parseUrl('/auth/login');
    }

    return true;
  }
}


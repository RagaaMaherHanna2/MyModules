import { Injectable } from '@angular/core';
import { CanMatch, Route, Router, UrlSegment, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanMatch {
  constructor(private router: Router) {}
  canMatch(
    route: Route,
    segments: UrlSegment[]
  ):
    | Observable<boolean | UrlTree>
    | Promise<boolean | UrlTree>
    | boolean
    | UrlTree {
      let first_login= JSON.parse(localStorage.getItem('first_login') || '{}')
    if (localStorage.getItem(environment.TOKEN_KEY) !==  undefined && !first_login){
      return true;
    
    }
    
    return this.router.parseUrl('/auth/login');
  }
}

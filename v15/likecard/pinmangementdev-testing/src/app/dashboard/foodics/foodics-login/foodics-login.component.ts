import { Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { FormBuilder, Validators } from '@angular/forms';
import { FoodicsService } from 'src/app/services/Foodics/foodics.service';
import { FoodicsLoginBody } from 'src/models/Foodics/models';
import { environment } from 'src/environments/environment';
import { Router } from '@angular/router';
@Component({
  selector: 'app-foodics-login',
  templateUrl: './foodics-login.component.html',
  styleUrls: ['./foodics-login.component.scss'],
})
export class FoodicsLoginComponent {
  constructor(
    private formBuilder: FormBuilder,
    private readonly store: Store<{}>,
    private foodicsService: FoodicsService,
    private router: Router
  ) {}
  loginForm = this.formBuilder.group({
    login: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });
  foodicsLoginBody: FoodicsLoginBody = {} as FoodicsLoginBody;

  login(): void {
    this.store.dispatch(openLoadingDialog());
    let values = this.loginForm.value;

    this.foodicsLoginBody.login = values.login as string;
    this.foodicsLoginBody.password = values.password as string;
    this.foodicsService.foodicsLogin(this.foodicsLoginBody).subscribe((res) => {
      if (res.ok) {
        localStorage.setItem(environment.TOKEN_KEY, res.result.token);
        this.router.navigate(['/foodics/connect']);
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }
}

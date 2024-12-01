import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FoodicsService } from 'src/app/services/Foodics/foodics.service';
import { environment } from 'src/environments/environment';
import { FoodicsNewBody } from 'src/models/Foodics/models';

@Component({
  selector: 'app-foodics-new',
  templateUrl: './foodics-new.component.html',
  styleUrls: ['./foodics-new.component.scss'],
})
export class FoodicsNewComponent {
  constructor(
    private router: ActivatedRoute,
    private foodicsService: FoodicsService
  ) {}
  successfullAuth: boolean = false;
  badAuth: boolean = false;

  foodicsNewBody: FoodicsNewBody = {} as FoodicsNewBody;
  ngOnInit() {
    this.router.queryParams.subscribe((queryParams) => {
      this.foodicsNewBody.code = queryParams['code'];
      this.foodicsNewBody.state = queryParams['state'];
    });
    this.foodicsService.foodicsNew(this.foodicsNewBody).subscribe((res) => {
      localStorage.removeItem(environment.TOKEN_KEY);
      if (res.ok) {
        this.successfullAuth == true;
      } else {
        this.badAuth == true;
      }
    });
  }
  goToGoogle() {}
}

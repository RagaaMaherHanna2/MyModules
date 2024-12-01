import { DOCUMENT } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { FoodicsService } from 'src/app/services/Foodics/foodics.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-foodics-connect',
  templateUrl: './foodics-connect.component.html',
  styleUrls: ['./foodics-connect.component.scss'],
})
export class FoodicsConnectComponent {
  constructor(
    private foodicsService: FoodicsService,
    @Inject(DOCUMENT) private document: Document
  ) {}

  disabled: boolean = false;
  preInstall() {
    this.disabled = true;
    this.foodicsService.preInstall().subscribe((res) => {
      this.disabled = false;
      if (res.ok) {
        this.document.location.href = res.result.redirect_url;
      }
    });
  }
}

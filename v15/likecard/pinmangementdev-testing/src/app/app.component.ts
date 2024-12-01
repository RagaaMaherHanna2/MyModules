import { Component, OnInit } from '@angular/core';
import { PrimeNGConfig } from 'primeng/api';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'Partner Dashboard';

  constructor(private primeConfig: PrimeNGConfig) {}

  ngOnInit(): void {
    if ($localize.locale === 'ar-AE') {
      this.primeConfig.setTranslation({
        choose: 'اختيار',
        cancel: 'الغاء',
        upload: 'رفع',
        dayNamesMin: ['أحـ', 'إثنـ', 'ثلثـ', 'أربـ', 'خميـ', 'جمعـ', 'سبـ'],
        monthNames: [
          'كانون الثاني',
          'شباط',
          'آذار',
          'نيسان',
          'أيار',
          'حزيران',
          'تموز',
          'آب',
          'أيلول',
          'تشرين الأول',
          'تشرين الثاني',
          'كانون الأول',
        ],
        monthNamesShort: [
          'كان2',
          'شب',
          'آذ',
          'نيس',
          'أيا',
          'حز',
          'تم',
          'آب',
          'أيل',
          'تش',
          'تش2',
          'كان1',
        ],
      });
    }
  }
}

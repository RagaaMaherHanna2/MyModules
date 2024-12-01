import { Component, OnInit } from '@angular/core';
import { Store, createSelector } from '@ngrx/store';
import { Subscription } from 'rxjs';
import { LayoutService } from 'src/app/services/layout.service';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss'],
})
export class StatisticsComponent implements OnInit {
  lineData: any;

  barData: any;

  lineOptions: any;

  barOptions: any;

  pieData: any;

  pieOptions: any;
  subscription: Subscription;

  constructor(public layoutService: LayoutService) {
    this.subscription = this.layoutService.configUpdate$.subscribe((config) => {
      this.initCharts();
    });
  }

  ngOnInit() {
    this.initCharts();
  }

  initCharts() {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue(
      '--text-color-secondary'
    );
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    this.barData = {
      labels: [
        'August',
        'September',
        'November',
        'October',
        'December',
        'January',
        'February',
      ],
      datasets: [
        {
          label: 'LC Balance',
          backgroundColor: documentStyle.getPropertyValue(
            '--theme-primary-800'
          ),
          borderColor: documentStyle.getPropertyValue('--theme-primary-800'),
          data: [165, 259, 180, 381, 456, 355, 440],
        },
        {
          label: 'LC Points',
          backgroundColor: documentStyle.getPropertyValue(
            '--theme-primary-500'
          ),
          borderColor: documentStyle.getPropertyValue('--theme-primary-500'),
          data: [265, 159, 380, 181, 256, 155, 340],
        },
        {
          label: 'LC Lucky',
          backgroundColor: documentStyle.getPropertyValue(
            '--theme-primary-200'
          ),
          borderColor: documentStyle.getPropertyValue('--theme-primary-200'),
          data: [228, 248, 340, 419, 286, 427, 390],
        },
      ],
    };

    this.barOptions = {
      plugins: {
        legend: {
          labels: {
            fontColor: textColor,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: textColorSecondary,
            font: {
              weight: 500,
            },
          },
          grid: {
            display: false,
            drawBorder: false,
          },
        },
        y: {
          ticks: {
            color: textColorSecondary,
          },
          grid: {
            color: surfaceBorder,
            drawBorder: false,
          },
        },
      },
    };

    this.lineData = {
      labels: [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31],
      datasets: [
        {
          label: $localize`This Month`,
          data: [133, 196, 125, 160, 132, 110, 170, 117, 171, 180, 190],
          fill: false,
          backgroundColor: documentStyle.getPropertyValue(
            '--theme-primary-500'
          ),
          borderColor: documentStyle.getPropertyValue('--theme-primary-500'),
          tension: 0.4,
        },
        {
          label: $localize`Previous Month`,
          data: [160, 178, 180, 171, 78, 184, 185, 104, 180, 150, 124, 133],
          fill: false,
          backgroundColor: documentStyle.getPropertyValue(
            '--theme-primary-200'
          ),
          borderColor: documentStyle.getPropertyValue('--theme-primary-200'),
          tension: 0.4,
        },
      ],
    };

    this.lineOptions = {
      plugins: {
        legend: {
          labels: {
            fontColor: textColor,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: textColorSecondary,
          },
          grid: {
            color: surfaceBorder,
            drawBorder: false,
          },
        },
        y: {
          ticks: {
            color: textColorSecondary,
          },
          grid: {
            color: surfaceBorder,
            drawBorder: false,
          },
        },
      },
    };
    this.pieData = {
      labels: ['LC Lucky', 'LC Balance', 'LC Points'],
      datasets: [
        {
          data: [1540, 1325, 1702],
          backgroundColor: [
            documentStyle.getPropertyValue('--theme-primary-200'),
            documentStyle.getPropertyValue('--theme-primary-800'),
            documentStyle.getPropertyValue('--theme-primary-500'),
          ],
          hoverBackgroundColor: [
            documentStyle.getPropertyValue('--theme-primary-100'),
            documentStyle.getPropertyValue('--theme-primary-700'),
            documentStyle.getPropertyValue('--theme-primary-400'),
          ],
        },
      ],
    };

    this.pieOptions = {
      plugins: {
        legend: {
          labels: {
            usePointStyle: true,
            color: textColor,
          },
        },
      },
    };
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}

import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { LayoutService } from 'src/app/services/layout.service';
import { AuthService } from 'src/app/services/auth.service';
import { Store, createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { MenuModule } from 'primeng/menu';
import { MenuItem, MessageService } from 'primeng/api';
import { balanceFeature } from 'src/store/balanceSlice';
import { environment } from 'src/environments/environment';
import { NotificationItem } from 'src/models/dashboard/layout.model';

@Component({
  selector: 'layout-top-bar',
  standalone: true,
  imports: [CommonModule, MenuModule],
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.scss'],
})
export class TopBarComponent implements OnInit {
  @ViewChild('sidebarButton') sidebarButton!: ElementRef;

  @ViewChild('topBarMenuButton') topBarMenuButton!: ElementRef;

  @ViewChild('topBarMenu') menu!: ElementRef;

  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || '';
  reference: string = '';
  balanceMenuModel: MenuItem[] = [
    {
      label: $localize`Balance Report`,
      routerLink: ['/dashboard/balance/report'],
    },
  ];
  userMenuModel: MenuItem[] = [];
  notificationsMenuModel: MenuItem[] = [];
  notifications: NotificationItem[] = [];

  isAllReaded: boolean = false;
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  user$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.user)
  );

  balance$ = this.store.select(
    createSelector(balanceFeature, (state) => state.balance)
  );
  isMerchant: boolean = false;
  constructor(
    public layoutService: LayoutService,
    private authService: AuthService,
    private store: Store,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.user$.subscribe((user) => {
      this.userMenuModel = [
        {
          label: `<div class="user"><p>${user.name}</p><span>${user.email}</span><div>`,
          escape: false,
        },
        {
          label: $localize`Logout`,
          command: () => {
            this.logout();
          },
          styleClass: 'logout-text',
        },
      ];
      if (user.roles.includes('merchant')) {
        this.isMerchant = true;
        this.userMenuModel.splice(1, 0, {
          label: user.reference,
          icon: 'pi pi-copy',
          command: () => {
            window.navigator.clipboard.writeText(user.reference!);
            this.messageService.add({
              summary: $localize`Copied`,
              detail: $localize`Reference copied`,
              severity: 'info',
            });
          },
          styleClass: 'reference',
        });
        return;
      }
      this.isMerchant = false;
    });

    this.authService.getALlNotifications().subscribe((res) => {
      this.notifications = res.result.data;
      this.fillNotificationsMenu();
    });
  }
  fillNotificationsMenu() {
    let datePipe: DatePipe = new DatePipe('en-US');
    let unReadedNotifications = this.notifications
      .filter((Notification) => Notification.is_read === false)
      .map((notify) => notify.id);
    if (this.notifications.length > 0) {
      this.notificationsMenuModel.push({
        items: [
          {
            label:
              unReadedNotifications.length > 0 && !this.isAllReaded
                ? '<div class= "flex-container"><span>' +
                  $localize`Notifications` +
                  '</span><u class="blue">' +
                  $localize`Mark all as read` +
                  '</u></div>'
                : '<div class= "flex-container"><span>' +
                  $localize`Notifications` +
                  '</span></div>',
            escape: false,
            command: () => {
              this.authService
                .markAllnotificationAsRead(unReadedNotifications)
                .subscribe((res) => {
                  if (res.ok) {
                    this.isAllReaded = true;
                    this.notificationsMenuModel = [];
                    this.fillNotificationsMenu();
                  }
                });
            },
          },
          {
            separator: true,
          },
        ],
      });
      for (let notification of this.notifications) {
        this.notificationsMenuModel[0].items?.push(
          {
            label:
              notification.body +
              '<p class="blue">' +
              datePipe.transform(notification.date, 'MM/dd/yyyy, hh:mm a'),
            escape: false,
            styleClass:
              !notification.is_read && !this.isAllReaded
                ? 'colored-notification'
                : '',
          },
          {
            separator: true,
          }
        );
      }
    } else {
      this.notificationsMenuModel.push({
        items: [{ label: $localize`No Notifications Yet`, escape: false }],
      });
    }
  }
  logout(): void {
    this.authService.logout();
  }
}

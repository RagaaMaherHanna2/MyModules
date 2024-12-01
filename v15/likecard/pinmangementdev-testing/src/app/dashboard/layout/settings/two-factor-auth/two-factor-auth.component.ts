import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { SettingsService } from 'src/app/services/settings/settings.service';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import { setUser } from 'src/store/accessRightSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { DomSanitizer } from '@angular/platform-browser';
import { MessageService } from 'primeng/api';
import { LOCALE_ID } from '@angular/core';

@Component({
  selector: 'app-two-factor-auth',
  templateUrl: './two-factor-auth.component.html',
  styleUrls: ['./two-factor-auth.component.scss'],
})
export class TwoFactorAuthComponent {
  enable2FaSteps: any[];
  refreshQrSteps: any[];
  enable2FaActiveIndex: number;
  refreshQrActiveIndex: number;
  imageSource: any;
  refresh_route: string = '';
  secret: string = '';
  OTP: any;
  VerficationCode: any;
  sendBtnDisabled: Boolean = true;
  sendVerficationCodeBtnDisabled: Boolean = true;
  isLoading: Boolean = true;
  is2FaEnabel: Boolean = false;
  enable2FaDialogVisible: boolean = false;
  refreshQrDialogVisible: boolean = false;
  currentLanguage: String = this.localeId;

  baseUrl: string = document.baseURI;

  constructor(
    private authService: AuthService,
    private store: Store,
    private sanitizer: DomSanitizer,
    private messageService: MessageService,
    @Inject(LOCALE_ID) private localeId: string
  ) {
    this.enable2FaSteps = [
      { label: $localize`Scan QR Code` },
      { label: $localize`Enter OTP` },
    ];
    this.refreshQrSteps = [
      { label: $localize`Enter Verification Code` },
      { label: $localize`Scan QR Code` },
      { label: $localize`Enter OTP` },
    ];
    this.enable2FaActiveIndex = 0;
    this.refreshQrActiveIndex = 0;
  }

  ngOnInit() {
    this.whoAmI();
    this.refresh_route = document.URL.replace(this.baseUrl, '');
  }
  whoAmI() {
    this.authService.whoAmI().subscribe((res) => {
      localStorage.setItem(
        environment.CODES_ADDITIONAL_VALUE,
        res.result.codes_additional_value
      );
      localStorage.setItem(
        environment.CURRENCY_SYMBOL,
        res.result.currency_symbol
      );

      localStorage.setItem(environment.USER_KEY, JSON.stringify(res.result));
      this.store.dispatch(setUser({ user: res.result }));
      this.store.dispatch(closeLoadingDialog());
      this.is2FaEnabel = res.result.totp_enabled;
      this.isLoading = false;
    });
  }

  onEnable2Fa() {
    this.store.dispatch(openLoadingDialog());
    this.authService.enable2f().subscribe((res) => {
      if (res.result) {
        this.store.dispatch(closeLoadingDialog());
        this.secret = res.result.secret;
        this.showEnable2FaDialog();
        this.imageSource = this.sanitizer.bypassSecurityTrustResourceUrl(
          `data:image/png;base64, ${res.result.qrcode}`
        );
      }
    });
  }

  sendEnableReq() {
    this.store.dispatch(openLoadingDialog());
    this.authService.active_enable2f(this.OTP, this.secret).subscribe((res) => {
      if (res.ok) {
        this.whoAmI();
        this.store.dispatch(closeLoadingDialog());
        this.enable2FaDialogVisible = false;
        this.onEnable2FaActiveIndexChange(0);
      }
    });
  }
  sendDisableReq() {
    this.store.dispatch(openLoadingDialog());

    this.authService.disable_2f().subscribe((res) => {
      if (res.ok) {
        this.store.dispatch(closeLoadingDialog());
        this.whoAmI();
        this.enable2FaDialogVisible = false;
        this.onEnable2FaActiveIndexChange(0);
      }
    });
  }

  showEnable2FaDialog() {
    this.enable2FaDialogVisible = true;
  }

  showRefreshQrDialog() {
    this.refreshQrDialogVisible = true;
  }

  onEnable2FaActiveIndexChange(event: number) {
    this.enable2FaActiveIndex = event;
  }
  onRefreshQrActiveIndexChange(event: number) {
    this.refreshQrActiveIndex = event;
  }

  onOtpChange(event: any) {
    this.OTP = event;
    this.sendBtnDisabled = !(this.OTP.length === 6);
  }

  onVerficationCodeChange(event: any) {
    this.VerficationCode = event;
    this.sendVerficationCodeBtnDisabled = !(this.VerficationCode.length === 6);
  }

  sendRefreshQrReq() {
    this.store.dispatch(openLoadingDialog());

    this.authService.refresh2f(this.refresh_route).subscribe((res) => {
      if (res.ok) {
        this.store.dispatch(closeLoadingDialog());
        this.showRefreshQrDialog();
        this.messageService.add({
          detail: `${res.message}`,
          icon: 'pi pi-check-circle',
          severity: 'info',
        });
      }
    });
  }

  activ_refresh2f() {
    this.store.dispatch(openLoadingDialog());
    this.authService.activ_refresh2f(this.VerficationCode).subscribe((res) => {
      if (res.ok) {
        this.secret = res.result.secret;
        this.imageSource = this.sanitizer.bypassSecurityTrustResourceUrl(
          `data:image/png;base64, ${res.result.qrcode}`
        );
        this.onRefreshQrActiveIndexChange(1);
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }

  activ_refresh2f_qr_code() {
    this.store.dispatch(openLoadingDialog());
    this.authService
      .activ_refresh2f_qr_code(this.OTP, this.secret)
      .subscribe((res) => {
        if (res.ok) {
          this.store.dispatch(closeLoadingDialog());
          this.refreshQrDialogVisible = false;
          this.onRefreshQrActiveIndexChange(0);
          this.secret = '';
          this.imageSource = '';
        }
      });
  }

  onDialogHide() {
    this.onEnable2FaActiveIndexChange(0);
    this.onRefreshQrActiveIndexChange(0);
    this.secret = '';
    this.imageSource = '';
  }
}

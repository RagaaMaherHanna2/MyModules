import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { WalletService } from 'src/app/services/wallet/wallet.service';
import { BankTransferRequest } from 'src/models/wallet/models';
import { confirmAction } from 'src/store/confirmationSlice';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-credit-request-details',
  templateUrl: './credit-request-details.component.html',
  styleUrls: ['./credit-request-details.component.scss'],
})
export class CreditRequestDetailsComponent implements OnInit {
  constructor(
    private activatedRoute: ActivatedRoute,
    private walletService: WalletService,
    private store: Store,
    private router: Router
  ) {}

  bankTransferRequest: BankTransferRequest;
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')
  note: string = '';
  readonly orderStatus: {
    [key: string]: any;
  } = {
    approved: {
      label: $localize`Approved`,
      severity: 'success',
    },
    draft: {
      label: $localize`Pending`,
      severity: 'warning',
    },
    rejected: {
      label: $localize`Rejected`,
      severity: 'danger',
    },
  };
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.walletService
        .getServiceProviderChargeRequestsDetails(+params['id'])
        .subscribe((res) => {
          if (res.ok) {
            this.bankTransferRequest = res.result.data[0];
          }
        });
    });
  }
  AcceptOrReject(state: string) {
    let message = $localize`Are you sure you want to accept this charge request?`;
    if (state !== 'approved')
      message = $localize`Are you sure you want to reject this charge request?`;
    this.store.dispatch(
      confirmAction({
        message: message,
        callbackFunction: () => {
          this.store.dispatch(openLoadingDialog());
          this.walletService
            .approveRejectBankRequest(
              this.bankTransferRequest.id,
              state,
              this.note
            )
            .subscribe((res) => {
              this.store.dispatch(closeLoadingDialog());
              if (res.ok) {
                this.router.navigate(['dashboard/wallet/view-credit-request']);
              }
            });
        },
      })
    );
  }
  downloadAttachment(item: BankTransferRequest): void {
    const link = document.createElement('a');
    link.href = `${environment.API_URL}${item.image}`;
    link.click();
    link.remove();
  }
}

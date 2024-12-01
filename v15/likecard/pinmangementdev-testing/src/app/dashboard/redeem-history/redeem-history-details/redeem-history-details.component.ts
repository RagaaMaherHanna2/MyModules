import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { RedeemService } from 'src/app/services/redeem/redeem.service';
import { environment } from 'src/environments/environment';
import { RedeemOperation } from 'src/models/Product/models';
import { RedeemHistoryWithFilter } from 'src/models/RedeemHistory/models';

@Component({
  selector: 'app-redeem-history-details',
  templateUrl: './redeem-history-details.component.html',
  styleUrls: ['./redeem-history-details.component.scss'],
})
export class RedeemHistoryDetailsComponent {
  redemptionOperation: RedeemOperation;
  redeemHistoryWithFilter: RedeemHistoryWithFilter;
  locale = $localize.locale;
  baseURL: string = environment.API_URL;

  constructor(
    private activatedRout: ActivatedRoute,
    private redeemService: RedeemService
  ) {}

  ngOnInit(): void {
    this.activatedRout.params.subscribe((params) => {
      this.redeemHistoryWithFilter = {
        serial: '',
        id: Number(params['id']),
        limit: 20,
        offset: 0,
      };
      this.redeemService
        .getRedeemHistory(this.redeemHistoryWithFilter)
        .subscribe((res) => {
          if (res.ok) {
            this.redemptionOperation = res.result.data[0];
          }
        });
    });
  }
}

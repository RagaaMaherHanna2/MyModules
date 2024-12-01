import {
  CreatePackage,
  GenerationRequest,
} from './../../../../models/package/models';
import { GetListResponse } from './../../../../models/responses/get-response.model';
import { BaseResponse } from './../../../../models/responses/base-response.model';
import { PackageService } from './../../../services/Package/package.service';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { CodeSeparator, CodeType, Package } from 'src/models/package/models';
import { Store } from '@ngrx/store';
import { confirmAction } from 'src/store/confirmationSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-package-details',
  templateUrl: './package-details.component.html',
  styleUrls: ['./package-details.component.scss'],
})
export class PackageDetailsComponent implements OnInit {
  package: Package = {} as Package;
  constructor(
    private activatedRoute: ActivatedRoute,
    private packageService: PackageService,
    private store: Store
  ) {}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      let input: any = { reference: id['reference'] };
      this.packageService
        .details(input)
        .subscribe((res: BaseResponse<GetListResponse<Package>>) => {
          this.package = res.result.data[0];
        });
    });
  }
  get_request_status_style(state: string) {
    switch (state) {
      case 'pending': {
        return 'warning';
      }
      case 'success': {
        return 'success';
      }
      case 'failed': {
        return 'danger';
      }
      case 'canceled': {
        return 'default';
      }
    }
    return 'default';
  }

  publishPackage(): void {
    this.store.dispatch(
      confirmAction({
        message: $localize`Are you sure you want to publish this package?`,
        callbackFunction: () => {
          this.store.dispatch(openLoadingDialog());
          const packageToPublish: Package = this.package;
          packageToPublish.state = 'published';
          this.packageService.edit(packageToPublish).subscribe((res) => {
            this.packageService
              .details({ reference: this.package.reference })
              .subscribe((res) => {
                this.package = res.result.data[0];

                this.store.dispatch(closeLoadingDialog());
              });
          });
        },
      })
    );
  }
}

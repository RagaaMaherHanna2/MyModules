import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { SubMerchantsService } from 'src/app/services/sub-merchants/sub-merchants.service';
// import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { MerchantsInviteList } from 'src/models/invites/invites.model';

@Component({
  selector: 'app-sub-merchant-details',
  templateUrl: './sub-merchant-details.component.html',
  styleUrls: ['./sub-merchant-details.component.scss'],
})
export class SubMerchantDetailsComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private subMerchantsService: SubMerchantsService,
    private store: Store,
    private messageService: MessageService,
  ) { }

  locale = $localize.locale;
  subMerchantData: MerchantsInviteList;
  permissionsCategories: any[] = [];
  listPermissions: any[] = [];
  selectedPermissions:any[] = [];



  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = +params['id'];
      if (id) {
        this.subMerchantsService.getSubMerchant(id).subscribe((res) => {
          if (res.ok) {
            this.subMerchantData = res.result.data.filter((item) => item.id === id)[0];

            this.subMerchantsService.getSubMerchantListPermissions(this.subMerchantData?.reference).subscribe ((res) => {
              if (res.ok) {
                console.log(res.result.data)
                if (res.result.data) {
                  this.listPermissions = res.result.data.map((p) => {
                    if (!this.permissionsCategories.includes(p.category)) {
                      this.permissionsCategories.push(p.category)
                    }
                    return {...p,label: $localize`${p.name_arabic}`}
                  } )
                  res.result.data.forEach(p => {
                    console.log(p)
                    if (p.enabled) {
                      this.selectedPermissions = [...this.selectedPermissions, p.id]
                    }
                  });
                }
              }
            })
          }
        });
      }
    });
  }

  assignPermission (codes: any[]) {
    console.log(codes)
    console.log(this.subMerchantData.reference)


    this.subMerchantsService.assignPermissionToSubmerchant(codes, this.subMerchantData?.reference).subscribe ((res) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: res.message,
          life: 3000,
        });
      }
    })
  }

  onPermissionsChange () {
    console.log(this.selectedPermissions)

  }

  submit(): void {
    const permissionsArray = this.listPermissions.map((p) => {
      return {
        code: p.code,
        enable: this.selectedPermissions.includes(p.id)
      }
    })
    this.assignPermission(permissionsArray)
  }
}

import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { SettingsService } from 'src/app/services/settings/settings.service';
import { environment } from 'src/environments/environment';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { spWebsiteKey, WebsiteName } from 'src/models/settings/settings';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-api-keys-management',
  templateUrl: './api-keys-management.component.html',
  styleUrls: ['./api-keys-management.component.scss'],
})
export class ApiKeysManagementComponent {
  constructor(
    private settingsService: SettingsService,
    private formBuilder: FormBuilder,
    private store: Store,
    private messageService: MessageService
  ) {}
  pageSize: number = environment.PAGE_SIZE;
  offset: number = 0;
  loading: boolean;
  filter: string = '';
  items: GetListResponse<spWebsiteKey> = { data: [], totalCount: 0 };
  showAddModal: boolean = false;
  apiKeyForm = this.formBuilder.group({
    website_name: ['', [Validators.required]],
  });
  addedWebsite: WebsiteName = { website_name: '' };
  ngOnInit(): void {
    this.loadApiKeys();
  }
  loadApiKeys() {
    this.loading = true;
    let body = {
      limit: environment.PAGE_SIZE,
      offset: this.offset,
      website_name: this.filter,
    };

    this.settingsService.getSpsWebsiteKeys(body).subscribe((res) => {
      if (res.ok) {
        this.items.data = res.result.data;
        this.items.totalCount = res.result.totalCount;
      }
      this.loading = false;
    });
  }
  addApiKey() {
    this.showAddModal = true;
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadApiKeys();
  }
  reiniApiKeyForm() {
    this.apiKeyForm.reset();
  }
  changePage(event: { first: number; rows: number }): void {
    this.offset = event.first;
    this.loadApiKeys();
  }

  submit() {
    this.store.dispatch(openLoadingDialog());
    console.log(this.apiKeyForm.value.website_name);
    this.addedWebsite.website_name = this.apiKeyForm.value.website_name;
    console.log(this.addedWebsite);
    this.settingsService
      .generateWebsiteKey(this.addedWebsite)
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: 'Successful',
            detail: $localize`API Key Generated Successfully`,
            life: 3000,
          });
          this.showAddModal = false;
          this.loadApiKeys();
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Generating API Key Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  copy(APIKey: string) {
    window.navigator.clipboard.writeText(APIKey);
    this.messageService.add({
      icon: 'pi pi-copy',
      summary: `Copied`,
      detail: `API Key Copied Successfully`,
      severity: 'info',
    });
  }
}

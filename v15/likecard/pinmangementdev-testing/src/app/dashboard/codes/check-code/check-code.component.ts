import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { CodeService } from 'src/app/services/Code/code.service';
import { PackageCode } from 'src/models/package/models';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { code } from 'src/models/serial/model';
@Component({
  selector: 'app-check-code',
  templateUrl: './check-code.component.html',
  styleUrls: ['./check-code.component.scss'],
})
export class CheckCodeComponent {
  codeForm = this.formBuilder.group({
    codes: ['', Validators.required],
  });

  locale = $localize.locale;
  codes: code[];
  constructor(
    private store: Store,
    private formBuilder: FormBuilder,
    private codeService: CodeService
  ) {}
  onSubmit(event: SubmitEvent): void {
    let codesList = this.codeForm.value.codes!.split(/\r?\n/);
    codesList = codesList.filter((code) => code.trim() !== '');
    this.store.dispatch(openLoadingDialog());
    this.codeService.check_codes({ codes: codesList }).subscribe((res) => {
      if (res.ok) {
        this.codes = res.result;
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }
}

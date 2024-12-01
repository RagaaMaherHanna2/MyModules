import { Component } from '@angular/core';
import { Validators, FormBuilder } from '@angular/forms';

@Component({
  selector: 'app-dashboard-settings',
  templateUrl: './dashboard-settings.component.html',
  styleUrls: ['./dashboard-settings.component.scss'],
})
export class DashboardSettingsComponent {
  settingsForm = this.formBuilder.group({
    language: [
      localStorage.getItem('dashboard_language') ?? '',
      Validators.required,
    ],
  });
  get language() {
    return this.settingsForm.get('language')!;
  }
  constructor(private formBuilder: FormBuilder) {}
  onSave(): void {
    localStorage.setItem('dashboard_language', this.language.value!);
    window.history.pushState(
      'change language',
      `localhost:4200/${this.language.value!}`
    );
  }
}

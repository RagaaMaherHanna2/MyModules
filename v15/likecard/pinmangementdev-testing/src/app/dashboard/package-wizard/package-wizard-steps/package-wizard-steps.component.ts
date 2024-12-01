import { Component } from '@angular/core';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-package-wizard-steps',
  templateUrl: './package-wizard-steps.component.html',
  styleUrls: ['./package-wizard-steps.component.scss']
})
export class PackageWizardStepsComponent {

  stepsModel: MenuItem[] = [
    {
      routerLink: 'create',
      label: $localize`Create Package`,
    },
    {
      routerLink: 'add-products',
      label: $localize`Add Products`,
    },
    {
      routerLink: 'invite-merchants',
      label: $localize`Invite Merchants`,
    },
    {
      routerLink: 'summary',
      label: $localize`Summary`
    }
  ]
}

import { Component, Input } from '@angular/core';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'shared-reference',
  templateUrl: './reference.component.html',
  styleUrls: ['./reference.component.scss']
})
export class ReferenceComponent {
  @Input() reference: string = ''


  constructor(private messageService: MessageService){}
  onCopy():void {
    window.navigator.clipboard.writeText(this.reference);
    this.messageService.add({
      icon: 'pi pi-copy' ,
      summary: $localize`Copied`,
      detail: $localize`Reference Copied`,
      severity: "info",
    })
  }
}

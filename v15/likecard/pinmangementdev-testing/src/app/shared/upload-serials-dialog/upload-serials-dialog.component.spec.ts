import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadSerialsDialogComponent } from './upload-serials-dialog.component';

describe('UploadSerialsDialogComponent', () => {
  let component: UploadSerialsDialogComponent;
  let fixture: ComponentFixture<UploadSerialsDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ UploadSerialsDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UploadSerialsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

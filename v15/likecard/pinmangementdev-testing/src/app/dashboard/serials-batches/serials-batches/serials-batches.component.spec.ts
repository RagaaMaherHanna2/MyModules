import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SerialsBatchesComponent } from './serials-batches.component';

describe('SerialsBatchesComponent', () => {
  let component: SerialsBatchesComponent;
  let fixture: ComponentFixture<SerialsBatchesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SerialsBatchesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SerialsBatchesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

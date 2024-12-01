import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OperationsHistoryComponent } from './operations-history.component';

describe('OperationsHistoryComponent', () => {
  let component: OperationsHistoryComponent;
  let fixture: ComponentFixture<OperationsHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OperationsHistoryComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OperationsHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

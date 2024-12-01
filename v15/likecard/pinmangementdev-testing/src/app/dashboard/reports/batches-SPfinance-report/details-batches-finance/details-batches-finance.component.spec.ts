import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailsBatchesFinanceComponent } from './details-batches-finance.component';

describe('DetailsBatchesFinanceComponent', () => {
  let component: DetailsBatchesFinanceComponent;
  let fixture: ComponentFixture<DetailsBatchesFinanceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DetailsBatchesFinanceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DetailsBatchesFinanceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { TestBed } from '@angular/core/testing';

import { FoodicsService } from './foodics.service';

describe('FoodicsService', () => {
  let service: FoodicsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FoodicsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

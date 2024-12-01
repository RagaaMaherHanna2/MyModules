import { TestBed } from '@angular/core/testing';

import { SubMerchantsService } from './sub-merchants.service';

describe('SubMerchantsService', () => {
  let service: SubMerchantsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SubMerchantsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RateLimit } from './rate-limit';

describe('RateLimit', () => {
  let component: RateLimit;
  let fixture: ComponentFixture<RateLimit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RateLimit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RateLimit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

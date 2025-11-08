import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecipeDeatail } from './recipe-deatail';

describe('RecipeDeatail', () => {
  let component: RecipeDeatail;
  let fixture: ComponentFixture<RecipeDeatail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecipeDeatail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecipeDeatail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecipeGrid } from './recipe-grid';

describe('RecipeGrid', () => {
  let component: RecipeGrid;
  let fixture: ComponentFixture<RecipeGrid>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecipeGrid]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecipeGrid);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

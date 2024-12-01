import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { CategoryService } from 'src/app/services/category/category.service';

import { environment } from 'src/environments/environment';
import { Category } from 'src/models/category/model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { confirmAction } from 'src/store/confirmationSlice';

@Component({
  selector: 'app-categories-list',
  templateUrl: './categories-list.component.html',
  styleUrls: ['./categories-list.component.scss'],
})
export class CategoriesListComponent implements OnInit {
  categories: GetListResponse<Category> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  locale = $localize.locale;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  constructor(
    private categoryService: CategoryService,
    private router: Router,
    private messageService: MessageService,
    private store: Store
  ) {}
  ngOnInit(): void {}

  editCategory(categoryId: number): void {}
  loadCategories(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.categoryService
      .getCategoryList({
        limit: this.pageSize,
        offset: event.first as number,
        name: this.filter,
        id: 0,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.categories = res.result;
          this.loading = false;
        } else {
          this.loading = false;
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Category Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  applyFilter(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.filter = target.value;
    const newFilterEvent: LazyLoadEvent = { first: 0, sortField: '' };
    this.loadCategories(newFilterEvent);
  }
  navigateToCreateCategoryPage() {
    this.router.navigate(['dashboard/category/create']);
  }
  goToEditPage(category: Category): void {
    this.router.navigate(['/dashboard/category/edit/', category.id]);
  }

  delete(category: Category) {
    if (category.product_count !== 0) {
      this.messageService.add({
        severity: 'error',
        summary: $localize`Unable to delete this category because it still contains products. Please delete products before trying again.`,
        life: 3000,
      });
    } else {
      this.store.dispatch(
        confirmAction({
          message: $localize`Are you sure you want to delete this category?`,
          callbackFunction: () => {
            this.categoryService
              .deleteCategory(category.id)
              .subscribe((res: BaseResponse<any>) => {
                if (res.ok) {
                  this.messageService.add({
                    severity: 'success',
                    summary: $localize`Successful`,
                    detail: $localize`Category Deleted Successfully`,
                    life: 3000,
                  });
                  let event: LazyLoadEvent = {};
                  event.first = 0;
                  event.sortField = '';
                  this.loadCategories(event);
                }
              });
          },
        })
      );
    }
  }
}

import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { CategoryService } from 'src/app/services/category/category.service';
import { environment } from 'src/environments/environment';
import { Category } from 'src/models/category/model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-edit-category',
  templateUrl: './edit-category.component.html',
  styleUrls: ['./edit-category.component.scss'],
})
export class EditCategoryComponent {
  categoryForm: FormGroup;
  category: Category;
  maxFileSizeMessage: string =
    $localize`Max file size ` +
    environment.MAX_UPLOADED_FILE_SIZE / 1000000 +
    $localize`MB`;
  constructor(
    private categoryService: CategoryService,
    private router: Router,
    private fb: FormBuilder,
    private messageService: MessageService,
    private readonly store: Store<{}>,
    private activatedRoute: ActivatedRoute
  ) {}
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      const categoryID: number = parseInt(id['id']);

      this.categoryService
        .getCategoryList({ limit: 1, offset: 0, name: '', id: categoryID })
        .subscribe((res) => {
          this.category = res.result.data[0];
          this.categoryForm = this.fb.group({
            id: [this.category.id, [Validators.required]],
            name: [this.category.name, [Validators.required]],
            name_ar: [this.category.name_ar, [Validators.required]],
            image: [this.category.image, [Validators.required]],
          });
        });
    });
  }
  onSubmit(): void {
    this.store.dispatch(openLoadingDialog());
    this.categoryService
      .editCategory(this.categoryForm.value)
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Successful`,
            detail: $localize`Category Edited Successfully`,
            life: 3000,
          });
          this.router.navigate(['dashboard/category/list']);
        }
      });
  }

  onUpload(event: any): void {
    const file = event?.files?.[0];
    if (!file) {
      console.error('No file selected');
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      const base64String = reader.result as string;
      const base64Data = base64String.split('base64,')[1] || '';
      this.categoryForm.patchValue({ image: base64Data });
    };

    reader.onerror = (error) => {
      console.error('Error reading file:', error);
    };

    reader.readAsDataURL(file);
  }

  onClear() {
    this.categoryForm.patchValue({ image: null });
  }
}

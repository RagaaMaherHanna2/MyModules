import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { CategoryService } from 'src/app/services/category/category.service';

import { environment } from 'src/environments/environment';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-create-category',
  templateUrl: './create-category.component.html',
  styleUrls: ['./create-category.component.scss'],
})
export class CreateCategoryComponent {
  categoryForm: FormGroup;

  maxFileSizeMessage: string =
    $localize`Max file size ` +
    environment.MAX_UPLOADED_FILE_SIZE / 1000000 +
    $localize`MB`;
  constructor(
    private categoryService: CategoryService,
    private router: Router,
    private fb: FormBuilder,
    private messageService: MessageService,
    private readonly store: Store<{}>
  ) {}
  ngOnInit(): void {
    this.categoryForm = this.fb.group({
      name: ['', [Validators.required]],
      name_ar: ['', [Validators.required]],
      image: [null, [Validators.required]], // null or empty for initial state
    });
  }
  onSubmit(): void {
    this.store.dispatch(openLoadingDialog());
    console.log('Form Value:', this.categoryForm.value);
    this.categoryService
      .createCategory(this.categoryForm.value)
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Successful`,
            detail: $localize`Category Created Successfully`,
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

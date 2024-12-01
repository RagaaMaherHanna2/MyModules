import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartModule } from 'primeng/chart';
import { ProductsRoutingModule } from './products-routing.module';
import { CreateProductComponent } from './create-product/create-product.component';
import { RadioButtonModule } from 'primeng/radiobutton';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { FileUploadModule } from 'primeng/fileupload';
import { MultiSelectModule } from 'primeng/multiselect';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ListProductsComponent } from './list-products/list-products.component';
import { TableModule } from 'primeng/table';
import { BadgeModule } from 'primeng/badge';
import { CheckboxModule } from 'primeng/checkbox';
import { EditProductComponent } from './edit-product/edit-product.component';
import { CardModule } from 'primeng/card';
import { DividerModule } from 'primeng/divider';
import { DialogModule } from 'primeng/dialog';
import { CalendarModule } from 'primeng/calendar';
import { ProductDetailsComponent } from './product-details/product-details.component';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { UploadSerialsDialogComponent } from 'src/app/shared/upload-serials-dialog/upload-serials-dialog.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { TriStateCheckboxModule } from 'primeng/tristatecheckbox';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { CategoriesListComponent } from '../categories/categories-list/categories-list.component';
import { CreateCategoryComponent } from '../categories/create-category/create-category.component';
import { MenuModule } from 'primeng/menu';
import { EditCategoryComponent } from '../categories/edit-category/edit-category.component';
@NgModule({
  declarations: [
    CreateProductComponent,
    ListProductsComponent,
    EditProductComponent,
    ProductDetailsComponent,
    CategoriesListComponent,
    CreateCategoryComponent,
    EditCategoryComponent,
  ],
  imports: [
    BadgeModule,
    CalendarModule,
    CardModule,
    CheckboxModule,
    CommonModule,
    DialogModule,
    DividerModule,
    DropdownModule,
    FileUploadModule,
    FormsModule,
    HttpClientModule,
    InputTextModule,
    MultiSelectModule,
    ProductsRoutingModule,
    ReactiveFormsModule,
    ProgressSpinnerModule,
    SharedModule,
    TableModule,
    UploadSerialsDialogComponent,
    ToggleButtonModule,
    RadioButtonModule,
    ChartModule,
    TriStateCheckboxModule,
    InputTextareaModule,
    MenuModule,
  ],
})
export class ProductsModule {}

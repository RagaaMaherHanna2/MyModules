import {
  Component,
  ViewChild,
  Input,
  Output,
  EventEmitter,
  AfterViewInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalendarModule } from 'primeng/calendar';
import { FileUpload, FileUploadModule } from 'primeng/fileupload';
import { environment } from 'src/environments/environment';
import { InsertedBatchSerial, Serial } from 'src/models/serial/model';
import { DialogModule } from 'primeng/dialog';
import { Store } from '@ngrx/store';
import { ProductService } from 'src/app/services/Product';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { MessageService } from 'primeng/api';
import { nanoid } from 'nanoid';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextareaModule } from 'primeng/inputtextarea';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { VendorsService } from 'src/app/services/vendors/vendors.service';
import { GetVendorsBody, Vendor } from 'src/models/vendors/vendor';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { DropdownModule } from 'primeng/dropdown';
import { AuthService } from 'src/app/services/auth.service';
import { Currency } from 'src/models/User';

@Component({
  selector: 'upload-serials-dialog',
  standalone: true,
  imports: [
    CommonModule,
    CalendarModule,
    FileUploadModule,
    DialogModule,
    InputTextModule,
    InputNumberModule,
    InputTextareaModule,
    FormsModule,
    ReactiveFormsModule,
    DropdownModule,
  ],
  templateUrl: './upload-serials-dialog.component.html',
  styleUrls: ['./upload-serials-dialog.component.scss'],
})
export class UploadSerialsDialogComponent implements AfterViewInit {
  @Input() dialogVisible: boolean = false;
  @Input() productInfo?: { id: number; SKU: string } = undefined;
  @Output() callback = new EventEmitter();
  @Output() dialogVisibleChange = new EventEmitter<boolean>();
  @ViewChild('serialsFileUploader') serialsFileUploader: FileUpload;

  selectedFile: any;
  readonly EXCEL_FILE_TYPES = environment.EXCEL_FILE_TYPES;
  error: string = '';
  insertedBatchSerial: InsertedBatchSerial;
  locale = $localize.locale;
  uploadSerialForm: FormGroup;
  vendors: GetListResponse<Vendor> = {
    totalCount: 0,
    data: [],
  };
  allCurrencies: Currency[];
  constructor(
    private store: Store,
    private productService: ProductService,
    private messageService: MessageService,
    private vendorsService: VendorsService,
    private authService: AuthService,
    private formBuilder: FormBuilder
  ) {
    this.uploadSerialForm = this.formBuilder.group({
      batch_sequence: new FormControl(nanoid(), [Validators.required]),
      product_id: new FormControl('', [Validators.required]),
      batch_file: new FormControl('', [Validators.required]),
      vendor_id: new FormControl(null, [Validators.required]),
      invoice_ref: new FormControl('', [Validators.required]),
      product_purchase_price: new FormControl('', [Validators.required]),
      batch_currency_id: new FormControl('', [Validators.required]),
      notes: new FormControl('', []),
    });
  }
  ngOnInit() {
    let body: GetVendorsBody = {
      limit: 10000,
      offset: 0,
      name: '',
    };

    this.vendorsService.getVendors(body).subscribe((res) => {
      if (res.ok) {
        this.vendors = res.result;
      }
    });
    this.getAllCurrencies();
  }

  ngAfterViewInit(): void {
    this.uploadSerialForm.patchValue({ product_id: this.productInfo?.id });
  }
  closeDialogAndClear(): void {
    this.serialsFileUploader.clear();
    this.uploadSerialForm.controls['notes'].reset();
    this.uploadSerialForm.controls['product_purchase_price'].reset();
    this.uploadSerialForm.controls['vendor_id'].reset();
    this.uploadSerialForm.controls['invoice_ref'].reset();
    this.uploadSerialForm.controls['batch_currency_id'].reset();
    this.dialogVisible = false;
    this.dialogVisibleChange.emit(this.dialogVisible);
  }
  onSelectFile(event: any): void {
    if (!event.currentFiles || event.currentFiles.length === 0) {
      return; // Exit if no file is selected
    }

    const reader = new FileReader();
    this.selectedFile = event.currentFiles[0];

    reader.readAsDataURL(this.selectedFile);

    reader.onload = () => {
      const result = reader.result as string;

      if (result) {
        const solution = result.split('base64,');
        if (solution.length > 1) {
          this.uploadSerialForm.patchValue({ batch_file: solution[1] });
        } else {
          console.error('File content is not in expected format.');
        }
      }
    };

    reader.onerror = (error) => {
      console.error('File reading has failed: ', error);
    };
  }

  clearFile(): void {
    this.uploadSerialForm.patchValue({ batch_file: '' });
  }

  onUploadSerials(): void {
    this.dialogVisible = false;
    this.store.dispatch(openLoadingDialog());
    this.insertedBatchSerial = this.uploadSerialForm.value;
    this.productService
      .insertSerials(this.insertedBatchSerial)
      .subscribe((res) => {
        if (res.ok) {
          this.callback.emit();
          this.store.dispatch(closeLoadingDialog());
          this.uploadSerialForm.patchValue({ batch_sequence: nanoid() });
          this.messageService.add({
            severity: 'success',
            summary: $localize`Successful`,
            detail: $localize`Your file is uploaded successfully and is being processed`,
            life: 3000,
          });
        }
      });
  }
  getAllCurrencies() {
    this.authService.getAllCurrencies().subscribe((res) => {
      if (res.ok) {
        this.allCurrencies = res.result.data;
      }
    });
  }
}

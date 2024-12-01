import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import { Serial } from 'src/models/serial/model';
import { openErrorDialog } from 'src/store/errorSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { read, utils, writeFile } from 'xlsx';
import { getJSONTime } from '../shared/utils/date';
import { Product } from 'src/models/Product/models';

@Injectable({
  providedIn: 'root',
})
export class ExcelService {
  constructor(private readonly store: Store) {}

  checkExcelColumns(row: any, product?: { id: number; SKU: string }): boolean {
    console.log(row, product);
    if (!row.A) {
      throw new Error($localize`Row #${row.__rowNum__ + 1} is missing serial`);
    }
    if (!row.B) {
      throw new Error($localize`Row #${row.__rowNum__ + 1} is missing SKU`);
    }
    if (!row.C) {
      throw new Error(
        $localize`Row #${row.__rowNum__ + 1} is missing Product ID`
      );
    }
    if (product) {
      if (`${product.SKU}` !== `${row.B}`) {
        throw new Error(
          $localize`Row #${row.__rowNum__ + 1} SKU(${
            row.B
          }) does not equal to product SKU (${product.SKU})`
        );
      }
      if (`${product.id}` !== `${row.C}`) {
        throw new Error(
          $localize`Row #${row.__rowNum__ + 1} ID(${
            row.C
          }) does not equal to product ID (${product.id})`
        );
      }
    }

    /* if (!row.D) {
      throw new Error(
        $localize`Row #${row.__rowNum__ + 1} is missing Expiry Date`
      );
    }
 */
    if (row.D && isNaN(Date.parse(row.D)) && isNaN(Date.parse(`${row.D}`))) {
      throw new Error(
        $localize`Row #${row.__rowNum__ + 1} has an invalid Expiry Date`
      );
    }
    /* if (!row.E) {
      throw new Error(
        $localize`Row #${row.__rowNum__ + 1} is
                   missing serial number`
      );
    } */
    return true;
  }
  uploadSerials(
    files: File[],
    product?: { id: number; SKU: string }
  ): Promise<Serial[]> {
    const generalErrorMessage = $localize`Please upload a valid Excel file, see template file for details`;
    return new Promise((resolve, reject) => {
      this.store.dispatch(openLoadingDialog());
      const file = files[0];
      try {
        if (!file) {
          throw new Error(generalErrorMessage);
        }
        const reader = new FileReader();
        reader.readAsArrayBuffer(file);
        reader.onload = (event) => {
          const data = event.target?.result;
          const workbook = read(data);
          const jsonData: any[] = utils.sheet_to_json(
            workbook.Sheets[workbook.SheetNames[0]],
            {
              blankrows: false,
              header: 'A',
              raw: true,
            }
          );

          const input: Serial[] = [];

          if (
            typeof jsonData[0]['A'] === 'string' &&
            jsonData[0]['A'].toLowerCase() === 'serial'
          ) {
            jsonData.shift();
          }
          try {
            if (Object.keys(jsonData[0]).length < 4) {
              throw new Error(generalErrorMessage);
            }
            jsonData.forEach((row) => {
              const serial: Serial = {} as Serial;
              if (this.checkExcelColumns(row, product)) {
                serial.serial_code = '' + row.A;
                serial.SKU = '' + row.B;
                serial.product_id = +row.C;
                if (row.D) {
                  serial.expiry_date = getJSONTime(row.D);
                }
                if (row.E) {
                  serial.serial_number = '' + row.E;
                }
              }
              input.push(serial);
            });
            this.store.dispatch(closeLoadingDialog());
            resolve(input);
          } catch (error) {
            if (error instanceof Error) {
              this.store.dispatch(closeLoadingDialog());
              this.store.dispatch(openErrorDialog({ message: error.message }));
              reject([]);
            }
          }
        };
      } catch (error) {
        if (error instanceof Error) {
          this.store.dispatch(closeLoadingDialog());
          this.store.dispatch(openErrorDialog({ message: error.message }));
          resolve([]);
        }
      }
    });
  }

  convertJSONtoExcel(
    data: Object[],
    headers: string[],
    filename: string,
    cellWidth: number = 20
  ): void {
    this.store.dispatch(openLoadingDialog());
    try {
      if (data.length < 1) {
        throw new Error($localize`There is no data to export to Excel file`);
      }
      data = data.map((item: any) => {
        if (item.hasOwnProperty('expiry_date')) {
          return {
            ...item,
            expiry_date: item.expiry_date
              ? new Date(item['expiry_date']).toLocaleDateString('en-GB')
              : $localize`No Expiry`,
          };
        } else {
          return item;
        }
      });
      const worksheet = utils.json_to_sheet(data);
      utils.sheet_add_aoa(worksheet, [headers], { origin: 'A1' });

      // Increasing columns width
      const widths: any = [];
      Object.keys(data[0]).forEach(() => {
        widths.push({ wch: cellWidth });
      });
      worksheet['!cols'] = widths;
      // END Increasing columns width

      const workbook = utils.book_new();
      utils.book_append_sheet(workbook, worksheet, 'Skarla Dashboard');

      this.store.dispatch(closeLoadingDialog());
      writeFile(workbook, `${filename}.xlsx`, {});
    } catch (error) {
      if (error instanceof Error) {
        this.store.dispatch(closeLoadingDialog());
        this.store.dispatch(openErrorDialog({ message: error.message }));
      }
    }
  }

  exportSerialTemplate(product: Product): void {
    const templateData = [
      {
        'Product name': product.name,
        Voucher: 'String (Alphanumeric)',
        SKU: product.SKU,
        'Product ID': product.id,
        'Expiry Date': 'Date',
        'Voucher Number': 'number',
      },
      {
        'Product name': 'It is the product name',
        Voucher: 'It is a unique number for each voucher',
        SKU: 'A unique identifier for the product',
        'Product ID':
          'A Unique number that represent the product id in the our system',
        'Expiry Date': `An expiration date, it must be Excel Date cell, or string with the format dd/mm/yyyy`,
        'Voucher Number':
          'Is a unique identifier assigned incrementally or sequentially to an item',
      },
      {
        'Product name': 'Optional',
        Voucher: 'Required',
        SKU: 'String, Required',
        'Product ID': 'Number, Required',
        'Expiry Date': 'Optional',
        'Voucher Number': 'Optional',
      },
    ];

    this.convertJSONtoExcel(templateData, [], $localize`Vouchers Template`, 40);
  }
}

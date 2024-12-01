import { environment } from 'src/environments/environment';
import {FormControl} from '@angular/forms';
export function fileSize( ) {
  return function (control: FormControl) {
    const file = control.value;
    if ( file ) {
      const size = file.size
      if ( size < environment.MAX_UPLOADED_FILE_SIZE ) {
        return {
          fileSize: true
        };
      }

      return null;
    }

    return null;
  };
}

import { FormControl } from '@angular/forms';
export function requiredImageType(types: string[]) {
  return function (control: FormControl) {
    const file = control.value;
    if (file) {
      const extension = file.name.split('.')[1].toLowerCase();
      if (
        types
          .map((type) => {
            return type.toLowerCase();
          })
          .includes(extension.toLowerCase())
      ) {
        return {
          requiredImageType: true,
        };
      }

      return null;
    }

    return null;
  };
}

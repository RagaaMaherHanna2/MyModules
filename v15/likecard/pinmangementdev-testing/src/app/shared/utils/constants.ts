export const ACTION_STATE: {
  [key: string]: {
    label:string,
    class: string,
  }
} = {
  pending: {
    label: $localize`Pending`,
    class: "warning"
  },
  success: {
    label: $localize`Successful`,
    class: "success"
  },
  done: {
    label: $localize`Successful`,
    class: "success"
  },
  failed: {
    label: $localize`Failed`,
    class: "danger"
  }
}

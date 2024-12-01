export interface BaseResponse<T> {
  message: string;
  ok: boolean;
  result: T;
}

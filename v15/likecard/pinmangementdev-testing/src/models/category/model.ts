export interface Category {
  id: number;
  name: string;
  image: string;
  name_ar: string;
  parent_id: number;
  product_count: number;
}

export interface CategoriesFilters {
  offset: number | undefined;
  limit: number | undefined;
  name: string | undefined;
  id: number | undefined;
}

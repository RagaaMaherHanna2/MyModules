export interface LayoutState {
  staticMenuDesktopInactive: boolean;
  overlayMenuActive: boolean;
  profileSidebarVisible: boolean;
  configSidebarVisible: boolean;
  staticMenuMobileActive: boolean;
  menuHoverActive: boolean;
}

export interface MenuChangeEvent {
  key: string;
  routeEvent?: boolean;
}
export interface AppConfig {
  inputStyle: string;
  colorScheme: string;
  theme: string;
  ripple: boolean;
  menuMode: string;
  scale: number;
}

export type NotificationItem = {
  id: number,
  date:string,
  subject: string,
  body: string,
  model:string,
  res_id: number,
  is_read: boolean
}

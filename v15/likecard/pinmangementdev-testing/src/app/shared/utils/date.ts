const englishLocale = 'en-GB';
const options: Intl.DateTimeFormatOptions = {
  dateStyle: 'short',
  timeStyle: 'short',
};
const validDateFormatPattern = /^\d{2}\/\d{2}\/\d{4}$/;

export function getFormattedDateTime(date: Date): string {
  return date.toLocaleString(englishLocale, options).replace(',', '');
}
export function getFormattedDate(date: Date): string {
  return date
    .toLocaleString(englishLocale, { dateStyle: options.dateStyle })
    .replace(',', '');
}
export function getISODate(date: Date): string {
  return date.toISOString();
}

export function getLocaleString(date: Date): string {
  return date.toLocaleString('default', {
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ...options,
  });
}

export function getJSONTime(date: string): string {
  if (!date && date === '') {
    return '';
  }
  if (validDateFormatPattern.test(date)) {
    return new Date(date).toISOString();
  }
  return new Date((+date - 25569) * 86400 * 1000).toISOString();
}

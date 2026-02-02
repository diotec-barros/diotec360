// Utility functions

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatHash(hash: string, length: number = 12): string {
  if (hash.length <= length) return hash;
  return `${hash.slice(0, length)}...`;
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

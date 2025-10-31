// Responsive breakpoints (matching Tailwind CSS)
export const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

// Check if current screen size matches breakpoint
export const useMediaQuery = (breakpoint: keyof typeof breakpoints): boolean => {
  if (typeof window === 'undefined') return false;
  
  return window.innerWidth >= breakpoints[breakpoint];
};

// Get current screen size category
export const getScreenSize = (): keyof typeof breakpoints | 'xs' => {
  if (typeof window === 'undefined') return 'xs';
  
  const width = window.innerWidth;
  
  if (width >= breakpoints['2xl']) return '2xl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  if (width >= breakpoints.sm) return 'sm';
  return 'xs';
};

// Mobile-first responsive utilities
export const isMobile = (): boolean => {
  return !useMediaQuery('md');
};

export const isTablet = (): boolean => {
  return useMediaQuery('md') && !useMediaQuery('lg');
};

export const isDesktop = (): boolean => {
  return useMediaQuery('lg');
};

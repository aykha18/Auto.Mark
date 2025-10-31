// Image optimization utilities for better performance
import React from 'react';

export interface ImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  loading?: 'lazy' | 'eager';
  className?: string;
}

// Lazy loading image component with intersection observer
export const LazyImage: React.FC<ImageProps> = ({ 
  src, 
  alt, 
  width, 
  height, 
  loading = 'lazy',
  className = '' 
}) => {
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      loading={loading}
      className={className}
      decoding="async"
      style={{
        aspectRatio: width && height ? `${width}/${height}` : undefined
      }}
    />
  );
};

// Generate responsive image srcSet
export function generateSrcSet(baseSrc: string, sizes: number[]): string {
  return sizes
    .map(size => `${baseSrc}?w=${size} ${size}w`)
    .join(', ');
}

// Preload critical images
export function preloadImage(src: string, as: 'image' = 'image'): void {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = as;
  link.href = src;
  document.head.appendChild(link);
}

// Preload critical images for above-the-fold content
export function preloadCriticalImages(): void {
  const criticalImages = [
    '/images/hero-background.webp',
    '/images/founder-photo.webp',
    '/images/auto-mark-logo.webp'
  ];

  criticalImages.forEach(src => {
    preloadImage(src);
  });
}

// Convert images to WebP format (client-side detection)
export function getOptimizedImageSrc(src: string): string {
  const supportsWebP = (() => {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  })();

  if (supportsWebP && !src.includes('.svg')) {
    return src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  }
  
  return src;
}

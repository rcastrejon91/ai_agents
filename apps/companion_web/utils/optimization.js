// utils/optimization.js

/**
 * Lazy load images when they come into viewport
 */
export const lazyLoadImages = () => {
  const images = document.querySelectorAll("img[data-src]");
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute("data-src");
        img.classList.add("loaded");
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: "50px 0px", // Start loading 50px before entering viewport
    threshold: 0.01
  });

  images.forEach((img) => imageObserver.observe(img));
};

/**
 * Dynamic import with error handling and retry logic
 */
export const dynamicImport = async (componentPath, maxRetries = 3) => {
  let attempt = 0;
  
  while (attempt < maxRetries) {
    try {
      const module = await import(`../components/${componentPath}`);
      return module.default;
    } catch (error) {
      attempt++;
      console.error(`Failed to load component: ${componentPath} (attempt ${attempt})`, error);
      
      if (attempt >= maxRetries) {
        throw new Error(`Failed to load component after ${maxRetries} attempts: ${componentPath}`);
      }
      
      // Wait before retrying (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
};

/**
 * Comprehensive performance monitoring
 */
export const setupPerformanceMonitoring = () => {
  if ("PerformanceObserver" in window) {
    // Monitor Core Web Vitals
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        switch (entry.entryType) {
          case "largest-contentful-paint":
            console.log("LCP:", entry.startTime);
            reportMetric("LCP", entry.startTime);
            break;
          case "first-input":
            console.log("FID:", entry.processingStart - entry.startTime);
            reportMetric("FID", entry.processingStart - entry.startTime);
            break;
          case "layout-shift":
            if (!entry.hadRecentInput) {
              console.log("CLS:", entry.value);
              reportMetric("CLS", entry.value);
            }
            break;
        }
      });
    });

    observer.observe({ entryTypes: ["largest-contentful-paint", "first-input", "layout-shift"] });
  }
};

/**
 * Resource preloading based on user interaction
 */
export const setupResourcePreloading = () => {
  const links = document.querySelectorAll('a[href]');
  
  links.forEach(link => {
    link.addEventListener('mouseenter', () => {
      preloadPage(link.href);
    }, { once: true });
  });
};

/**
 * Preload a page's critical resources
 */
const preloadPage = (url) => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  document.head.appendChild(link);
};

/**
 * Report performance metrics to analytics
 */
const reportMetric = (name, value) => {
  // Send to analytics service if available
  if (window.gtag) {
    window.gtag('event', name, {
      value: Math.round(value),
      custom_parameter_1: navigator.connection?.effectiveType || 'unknown'
    });
  }
  
  // Can also send to custom analytics endpoint
  if (window.analytics && typeof window.analytics.track === 'function') {
    window.analytics.track('Performance Metric', {
      metric: name,
      value: value,
      url: window.location.href,
      userAgent: navigator.userAgent,
      connection: navigator.connection?.effectiveType || 'unknown'
    });
  }
};

/**
 * Optimize images by setting appropriate loading attributes
 */
export const optimizeImages = () => {
  const images = document.querySelectorAll('img');
  
  images.forEach((img, index) => {
    // Add loading="lazy" to images below the fold
    if (index > 2) {
      img.loading = 'lazy';
    }
    
    // Add decoding="async" for better performance
    img.decoding = 'async';
    
    // Set appropriate fetchpriority
    if (index === 0) {
      img.fetchPriority = 'high';
    } else if (index < 3) {
      img.fetchPriority = 'auto';
    } else {
      img.fetchPriority = 'low';
    }
  });
};

/**
 * Service worker registration for caching
 */
export const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('ServiceWorker registration successful:', registration);
      return registration;
    } catch (error) {
      console.error('ServiceWorker registration failed:', error);
    }
  }
};

/**
 * Memory usage monitoring
 */
export const monitorMemoryUsage = () => {
  if ('memory' in performance) {
    const memory = performance.memory;
    console.log('Memory usage:', {
      used: Math.round(memory.usedJSHeapSize / 1048576) + 'MB',
      total: Math.round(memory.totalJSHeapSize / 1048576) + 'MB',
      limit: Math.round(memory.jsHeapSizeLimit / 1048576) + 'MB'
    });
    
    // Report high memory usage
    if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.9) {
      console.warn('High memory usage detected');
      reportMetric('HighMemoryUsage', memory.usedJSHeapSize / memory.jsHeapSizeLimit);
    }
  }
};

/**
 * Initialize all optimizations
 */
export const initOptimizations = () => {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      lazyLoadImages();
      optimizeImages();
      setupResourcePreloading();
    });
  } else {
    lazyLoadImages();
    optimizeImages();
    setupResourcePreloading();
  }
  
  // Setup performance monitoring
  setupPerformanceMonitoring();
  
  // Monitor memory usage periodically
  setInterval(monitorMemoryUsage, 30000); // Every 30 seconds
  
  // Register service worker
  registerServiceWorker();
};

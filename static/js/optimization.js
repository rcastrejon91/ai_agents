/**
 * Frontend optimization utilities for the main application
 * This is a simplified version for environments without ES6 modules
 */

(function() {
  'use strict';

  // Namespace for optimization functions
  window.Optimization = window.Optimization || {};

  /**
   * Lazy load images when they come into viewport
   */
  window.Optimization.lazyLoadImages = function() {
    var images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
      var imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            img.classList.add('loaded');
            imageObserver.unobserve(img);
          }
        });
      }, {
        rootMargin: '50px 0px',
        threshold: 0.01
      });

      images.forEach(function(img) {
        imageObserver.observe(img);
      });
    } else {
      // Fallback for browsers without IntersectionObserver
      images.forEach(function(img) {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
    }
  };

  /**
   * Optimize images by setting appropriate loading attributes
   */
  window.Optimization.optimizeImages = function() {
    var images = document.querySelectorAll('img');
    
    images.forEach(function(img, index) {
      // Add loading="lazy" to images below the fold
      if (index > 2 && 'loading' in HTMLImageElement.prototype) {
        img.loading = 'lazy';
      }
      
      // Add decoding="async" for better performance
      if ('decoding' in img) {
        img.decoding = 'async';
      }
    });
  };

  /**
   * Setup performance monitoring
   */
  window.Optimization.setupPerformanceMonitoring = function() {
    if ('PerformanceObserver' in window) {
      try {
        var observer = new PerformanceObserver(function(list) {
          list.getEntries().forEach(function(entry) {
            switch (entry.entryType) {
              case 'largest-contentful-paint':
                console.log('LCP:', entry.startTime);
                window.Optimization.reportMetric('LCP', entry.startTime);
                break;
              case 'first-input':
                console.log('FID:', entry.processingStart - entry.startTime);
                window.Optimization.reportMetric('FID', entry.processingStart - entry.startTime);
                break;
              case 'layout-shift':
                if (!entry.hadRecentInput) {
                  console.log('CLS:', entry.value);
                  window.Optimization.reportMetric('CLS', entry.value);
                }
                break;
            }
          });
        });

        observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
      } catch (e) {
        console.warn('Performance monitoring setup failed:', e);
      }
    }
  };

  /**
   * Report performance metrics
   */
  window.Optimization.reportMetric = function(name, value) {
    // Send to analytics if available
    if (window.gtag && typeof window.gtag === 'function') {
      window.gtag('event', name, {
        value: Math.round(value),
        custom_parameter_1: navigator.connection ? navigator.connection.effectiveType : 'unknown'
      });
    }
    
    // Custom analytics tracking
    if (window.analytics && typeof window.analytics.track === 'function') {
      window.analytics.track('Performance Metric', {
        metric: name,
        value: value,
        url: window.location.href,
        userAgent: navigator.userAgent,
        connection: navigator.connection ? navigator.connection.effectiveType : 'unknown'
      });
    }
  };

  /**
   * Service worker registration
   */
  window.Optimization.registerServiceWorker = function() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(function(registration) {
          console.log('ServiceWorker registration successful:', registration);
          return registration;
        })
        .catch(function(error) {
          console.error('ServiceWorker registration failed:', error);
        });
    }
  };

  /**
   * Memory usage monitoring
   */
  window.Optimization.monitorMemoryUsage = function() {
    if (performance.memory) {
      var memory = performance.memory;
      console.log('Memory usage:', {
        used: Math.round(memory.usedJSHeapSize / 1048576) + 'MB',
        total: Math.round(memory.totalJSHeapSize / 1048576) + 'MB',
        limit: Math.round(memory.jsHeapSizeLimit / 1048576) + 'MB'
      });
      
      // Report high memory usage
      if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.9) {
        console.warn('High memory usage detected');
        window.Optimization.reportMetric('HighMemoryUsage', memory.usedJSHeapSize / memory.jsHeapSizeLimit);
      }
    }
  };

  /**
   * Initialize all optimizations
   */
  window.Optimization.init = function() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        window.Optimization.lazyLoadImages();
        window.Optimization.optimizeImages();
      });
    } else {
      window.Optimization.lazyLoadImages();
      window.Optimization.optimizeImages();
    }
    
    // Setup performance monitoring
    window.Optimization.setupPerformanceMonitoring();
    
    // Monitor memory usage periodically
    setInterval(window.Optimization.monitorMemoryUsage, 30000); // Every 30 seconds
    
    // Register service worker
    window.Optimization.registerServiceWorker();
  };

  // Auto-initialize when script loads
  window.Optimization.init();

})();
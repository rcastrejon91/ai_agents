/**
 * Frontend Performance Optimization Module
 * 
 * This module provides comprehensive frontend performance optimizations including:
 * - Resource loading optimization
 * - DOM manipulation performance
 * - Memory management
 * - Event delegation and throttling
 * - Image lazy loading
 * - Cache management
 * - Bundle size optimization
 */

(function(window, document) {
    'use strict';

    // Performance optimization utility object
    const OptimizationEngine = {
        
        // Configuration options
        config: {
            lazyLoadOffset: 50,
            throttleDelay: 16, // ~60fps
            debounceDelay: 300,
            cacheExpiry: 30 * 60 * 1000, // 30 minutes
            enableLogging: true,
            enableMetrics: true
        },

        // Performance metrics collection
        metrics: {
            domOperations: 0,
            networkRequests: 0,
            cacheHits: 0,
            cacheMisses: 0,
            lazyLoadedImages: 0,
            startTime: performance.now()
        },

        // Simple cache implementation
        cache: new Map(),

        /**
         * Initialize the optimization engine
         */
        init() {
            this.log('🚀 Initializing Frontend Optimization Engine');
            
            // Set up performance observers
            this.setupPerformanceObservers();
            
            // Initialize lazy loading
            this.initLazyLoading();
            
            // Setup event delegation
            this.setupEventDelegation();
            
            // Initialize resource preloading
            this.initResourcePreloading();
            
            // Setup viewport optimizations
            this.setupViewportOptimizations();
            
            // Initialize memory management
            this.initMemoryManagement();
            
            this.log('✅ Optimization engine initialized');
        },

        /**
         * Logging utility
         */
        log(message, data) {
            if (this.config.enableLogging) {
                console.log(`[OptimizationEngine] ${message}`, data || '');
            }
        },

        /**
         * Setup performance observers for monitoring
         */
        setupPerformanceObservers() {
            if ('PerformanceObserver' in window) {
                // Monitor Long Task API
                try {
                    const longTaskObserver = new PerformanceObserver((list) => {
                        list.getEntries().forEach((entry) => {
                            if (entry.duration > 50) {
                                this.log(`⚠️ Long task detected: ${entry.duration}ms`, entry);
                            }
                        });
                    });
                    longTaskObserver.observe({ entryTypes: ['longtask'] });
                } catch (e) {
                    this.log('Long task observer not supported');
                }

                // Monitor layout shifts
                try {
                    const clsObserver = new PerformanceObserver((list) => {
                        list.getEntries().forEach((entry) => {
                            if (entry.hadRecentInput) return;
                            if (entry.value > 0.1) {
                                this.log(`⚠️ Layout shift detected: ${entry.value}`, entry);
                            }
                        });
                    });
                    clsObserver.observe({ entryTypes: ['layout-shift'] });
                } catch (e) {
                    this.log('Layout shift observer not supported');
                }
            }
        },

        /**
         * Initialize lazy loading for images and other resources
         */
        initLazyLoading() {
            if ('IntersectionObserver' in window) {
                const imageObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            if (img.dataset.src) {
                                img.src = img.dataset.src;
                                img.removeAttribute('data-src');
                                imageObserver.unobserve(img);
                                this.metrics.lazyLoadedImages++;
                                this.log(`📷 Lazy loaded image: ${img.src}`);
                            }
                        }
                    });
                }, {
                    rootMargin: `${this.config.lazyLoadOffset}px`
                });

                // Observe all images with data-src
                document.querySelectorAll('img[data-src]').forEach(img => {
                    imageObserver.observe(img);
                });

                // Set up observer for dynamically added images
                this.observeNewImages = (img) => imageObserver.observe(img);
            } else {
                // Fallback for older browsers
                this.loadAllImages();
            }
        },

        /**
         * Load all images immediately (fallback)
         */
        loadAllImages() {
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        },

        /**
         * Setup efficient event delegation
         */
        setupEventDelegation() {
            // Throttled scroll handler
            let scrollTimeout;
            const throttledScrollHandler = this.throttle(() => {
                // Handle scroll events efficiently
                this.handleScroll();
            }, this.config.throttleDelay);

            // Debounced resize handler
            const debouncedResizeHandler = this.debounce(() => {
                this.handleResize();
            }, this.config.debounceDelay);

            // Add optimized event listeners
            document.addEventListener('scroll', throttledScrollHandler, { passive: true });
            window.addEventListener('resize', debouncedResizeHandler, { passive: true });

            // Efficient click delegation
            document.addEventListener('click', (e) => {
                this.handleDelegatedClick(e);
            }, { passive: false });
        },

        /**
         * Handle scroll events efficiently
         */
        handleScroll() {
            // Implement scroll-based optimizations
            const scrollY = window.pageYOffset;
            
            // Update header state based on scroll position
            const header = document.querySelector('header');
            if (header) {
                if (scrollY > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
        },

        /**
         * Handle resize events efficiently
         */
        handleResize() {
            // Implement responsive optimizations
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight
            };

            // Adjust layout for mobile/desktop
            document.body.setAttribute('data-viewport', 
                viewport.width < 768 ? 'mobile' : 
                viewport.width < 1024 ? 'tablet' : 'desktop'
            );
        },

        /**
         * Handle delegated click events
         */
        handleDelegatedClick(event) {
            const target = event.target;
            
            // Handle lazy loading trigger clicks
            if (target.matches('[data-lazy-trigger]')) {
                this.triggerLazyLoad(target);
                event.preventDefault();
            }

            // Handle cache clear buttons
            if (target.matches('[data-clear-cache]')) {
                this.clearCache();
                event.preventDefault();
            }
        },

        /**
         * Initialize resource preloading
         */
        initResourcePreloading() {
            // Preload critical resources
            const criticalResources = [
                { href: '/api/health', as: 'fetch' },
                // Add more critical resources as needed
            ];

            criticalResources.forEach(resource => {
                if (resource.href) {
                    this.preloadResource(resource.href, resource.as);
                }
            });
        },

        /**
         * Preload a specific resource
         */
        preloadResource(href, as = 'fetch') {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = href;
            link.as = as;
            
            if (as === 'fetch') {
                link.crossOrigin = 'anonymous';
            }
            
            document.head.appendChild(link);
            this.log(`🔗 Preloading resource: ${href}`);
        },

        /**
         * Setup viewport-specific optimizations
         */
        setupViewportOptimizations() {
            // Set initial viewport data
            this.handleResize();

            // Optimize for touch devices
            if ('ontouchstart' in window) {
                document.body.classList.add('touch-device');
                
                // Remove hover states on touch devices
                const style = document.createElement('style');
                style.textContent = `
                    @media (hover: none) {
                        .hover\\:hover { display: none !important; }
                    }
                `;
                document.head.appendChild(style);
            }
        },

        /**
         * Initialize memory management
         */
        initMemoryManagement() {
            // Clean up unused resources periodically
            setInterval(() => {
                this.cleanupMemory();
            }, 5 * 60 * 1000); // Every 5 minutes

            // Handle page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.pauseNonEssentialOperations();
                } else {
                    this.resumeOperations();
                }
            });
        },

        /**
         * Clean up memory and unused resources
         */
        cleanupMemory() {
            // Clear expired cache entries
            const now = Date.now();
            for (const [key, value] of this.cache.entries()) {
                if (value.expiry < now) {
                    this.cache.delete(key);
                }
            }

            // Force garbage collection if available
            if (window.gc && typeof window.gc === 'function') {
                window.gc();
            }

            this.log('🧹 Memory cleanup completed');
        },

        /**
         * Pause non-essential operations when page is hidden
         */
        pauseNonEssentialOperations() {
            this.log('⏸️ Pausing non-essential operations');
            // Stop animations, timers, etc.
        },

        /**
         * Resume operations when page becomes visible
         */
        resumeOperations() {
            this.log('▶️ Resuming operations');
            // Resume animations, timers, etc.
        },

        /**
         * Efficient cache implementation
         */
        setCache(key, value, expiry = this.config.cacheExpiry) {
            this.cache.set(key, {
                value,
                expiry: Date.now() + expiry
            });
        },

        getCache(key) {
            const cached = this.cache.get(key);
            if (cached && cached.expiry > Date.now()) {
                this.metrics.cacheHits++;
                return cached.value;
            }
            this.metrics.cacheMisses++;
            this.cache.delete(key);
            return null;
        },

        clearCache() {
            this.cache.clear();
            this.log('🗑️ Cache cleared');
        },

        /**
         * Optimized fetch wrapper with caching
         */
        async optimizedFetch(url, options = {}) {
            const cacheKey = `fetch_${url}_${JSON.stringify(options)}`;
            
            // Check cache first
            const cached = this.getCache(cacheKey);
            if (cached) {
                this.log(`💾 Cache hit for: ${url}`);
                return cached;
            }

            // Perform fetch
            try {
                this.metrics.networkRequests++;
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'X-Requested-With': 'OptimizationEngine',
                        ...options.headers
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.setCache(cacheKey, data);
                    this.log(`🌐 Fetched and cached: ${url}`);
                    return data;
                }
                
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            } catch (error) {
                this.log(`❌ Fetch error for ${url}:`, error);
                throw error;
            }
        },

        /**
         * Optimized DOM manipulation
         */
        optimizedDOMUpdate(callback) {
            this.metrics.domOperations++;
            
            // Use requestAnimationFrame for DOM updates
            return new Promise(resolve => {
                requestAnimationFrame(() => {
                    const result = callback();
                    resolve(result);
                });
            });
        },

        /**
         * Throttle function calls
         */
        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * Debounce function calls
         */
        debounce(func, delay) {
            let timeoutId;
            return function() {
                const args = arguments;
                const context = this;
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(context, args), delay);
            };
        },

        /**
         * Trigger lazy loading for a specific element
         */
        triggerLazyLoad(element) {
            if (this.observeNewImages && element.tagName === 'IMG' && element.dataset.src) {
                this.observeNewImages(element);
            }
        },

        /**
         * Get performance metrics
         */
        getMetrics() {
            return {
                ...this.metrics,
                uptime: performance.now() - this.metrics.startTime,
                cacheSize: this.cache.size,
                memoryUsage: performance.memory ? {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                } : null
            };
        },

        /**
         * Export metrics for monitoring
         */
        exportMetrics() {
            if (this.config.enableMetrics) {
                const metrics = this.getMetrics();
                this.log('📊 Performance Metrics:', metrics);
                return metrics;
            }
            return null;
        },

        /**
         * Advanced bundle optimization techniques
         */
        optimizeBundle() {
            // Code splitting simulation
            this.loadModuleOnDemand = async (moduleName) => {
                try {
                    const cacheKey = `module_${moduleName}`;
                    let module = this.getCache(cacheKey);
                    
                    if (!module) {
                        // Simulate dynamic import
                        this.log(`📦 Loading module on demand: ${moduleName}`);
                        module = await import(`./${moduleName}.js`);
                        this.setCache(cacheKey, module);
                    }
                    
                    return module;
                } catch (error) {
                    this.log(`❌ Failed to load module ${moduleName}:`, error);
                    return null;
                }
            };
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            OptimizationEngine.init();
        });
    } else {
        OptimizationEngine.init();
    }

    // Expose to global scope for external access
    window.OptimizationEngine = OptimizationEngine;

    // Performance monitoring endpoint
    window.getPerformanceMetrics = () => OptimizationEngine.exportMetrics();

    // Utility functions for external use
    window.optimizedFetch = (url, options) => OptimizationEngine.optimizedFetch(url, options);
    window.optimizedDOMUpdate = (callback) => OptimizationEngine.optimizedDOMUpdate(callback);

})(window, document);

// Service Worker registration for advanced caching
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('[OptimizationEngine] Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('[OptimizationEngine] Service Worker registration failed:', error);
            });
    });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.OptimizationEngine;
}
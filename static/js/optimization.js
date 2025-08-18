/**
 * Frontend Optimization Module
 * Implements lazy loading, code splitting, and performance optimizations
 */

// Lazy loading for images
document.addEventListener('DOMContentLoaded', () => {
    initializeLazyLoading();
    initializeCodeSplitting();
    initializePerformanceOptimizations();
});

/**
 * Initialize intersection observer for lazy loading images
 */
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Create a new image to preload
                    const newImg = new Image();
                    newImg.onload = () => {
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        img.removeAttribute('data-src');
                    };
                    newImg.onerror = () => {
                        img.classList.add('error');
                        console.warn('Failed to load image:', img.dataset.src);
                    };
                    newImg.src = img.dataset.src;
                    
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });
        
        images.forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

/**
 * Code splitting utilities
 */
const moduleCache = new Map();

/**
 * Dynamically load a component with caching
 * @param {string} name - Component name
 * @returns {Promise} - Component module
 */
export const loadComponent = async (name) => {
    // Check cache first
    if (moduleCache.has(name)) {
        return moduleCache.get(name);
    }
    
    try {
        // Add loading indicator if element exists
        const loadingElement = document.querySelector(`[data-component="${name}"]`);
        if (loadingElement) {
            loadingElement.classList.add('loading');
        }
        
        const module = await import(`./components/${name}.js`);
        
        // Cache the module
        moduleCache.set(name, module.default || module);
        
        // Remove loading indicator
        if (loadingElement) {
            loadingElement.classList.remove('loading');
        }
        
        return module.default || module;
    } catch (error) {
        console.error(`Failed to load component: ${name}`, error);
        
        // Show error state
        const errorElement = document.querySelector(`[data-component="${name}"]`);
        if (errorElement) {
            errorElement.classList.add('error');
            errorElement.innerHTML = '<p>Failed to load component</p>';
        }
        
        throw error;
    }
};

/**
 * Load component when element comes into view
 * @param {string} componentName - Name of the component to load
 * @param {string} selector - CSS selector for the element
 */
export const loadComponentOnView = (componentName, selector) => {
    const elements = document.querySelectorAll(selector);
    
    if ('IntersectionObserver' in window) {
        const componentObserver = new IntersectionObserver((entries) => {
            entries.forEach(async (entry) => {
                if (entry.isIntersecting) {
                    try {
                        const component = await loadComponent(componentName);
                        
                        // Initialize component if it has an init method
                        if (component && typeof component.init === 'function') {
                            component.init(entry.target);
                        }
                        
                        componentObserver.unobserve(entry.target);
                    } catch (error) {
                        console.error(`Failed to initialize component ${componentName}:`, error);
                    }
                }
            });
        }, {
            rootMargin: '100px 0px',
            threshold: 0.1
        });
        
        elements.forEach(el => componentObserver.observe(el));
    } else {
        // Fallback: load immediately
        elements.forEach(async (el) => {
            const component = await loadComponent(componentName);
            if (component && typeof component.init === 'function') {
                component.init(el);
            }
        });
    }
};

/**
 * Initialize code splitting for components marked with data-component
 */
function initializeCodeSplitting() {
    const componentElements = document.querySelectorAll('[data-component]');
    
    componentElements.forEach(element => {
        const componentName = element.dataset.component;
        const loadTrigger = element.dataset.loadTrigger || 'view'; // 'view', 'click', 'hover'
        
        if (loadTrigger === 'view') {
            loadComponentOnView(componentName, `[data-component="${componentName}"]`);
        } else if (loadTrigger === 'click') {
            element.addEventListener('click', async () => {
                const component = await loadComponent(componentName);
                if (component && typeof component.init === 'function') {
                    component.init(element);
                }
            }, { once: true });
        } else if (loadTrigger === 'hover') {
            element.addEventListener('mouseenter', async () => {
                const component = await loadComponent(componentName);
                if (component && typeof component.init === 'function') {
                    component.init(element);
                }
            }, { once: true });
        }
    });
}

/**
 * Performance optimizations
 */
function initializePerformanceOptimizations() {
    // Debounce scroll events
    let scrollTimeout;
    const scrollHandlers = [];
    
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            cancelAnimationFrame(scrollTimeout);
        }
        
        scrollTimeout = requestAnimationFrame(() => {
            scrollHandlers.forEach(handler => handler());
        });
    }, { passive: true });
    
    // Debounce resize events
    let resizeTimeout;
    const resizeHandlers = [];
    
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            resizeHandlers.forEach(handler => handler());
        }, 250);
    });
    
    // Prefetch links on hover
    const prefetchedLinks = new Set();
    
    document.addEventListener('mouseover', (e) => {
        if (e.target.tagName === 'A' && e.target.href) {
            const href = e.target.href;
            
            if (!prefetchedLinks.has(href) && 
                href.startsWith(window.location.origin)) {
                
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = href;
                document.head.appendChild(link);
                
                prefetchedLinks.add(href);
            }
        }
    });
    
    // Resource hints
    addResourceHints();
    
    // Initialize web vitals monitoring
    initializeWebVitals();
}

/**
 * Add resource hints for better performance
 */
function addResourceHints() {
    const hints = [
        { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
        { rel: 'dns-prefetch', href: '//api.openai.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }
    ];
    
    hints.forEach(hint => {
        const link = document.createElement('link');
        Object.assign(link, hint);
        document.head.appendChild(link);
    });
}

/**
 * Initialize Web Vitals monitoring
 */
function initializeWebVitals() {
    // Monitor Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            
            console.log('LCP:', lastEntry.startTime);
            
            // Send to analytics if available
            if (window.gtag) {
                window.gtag('event', 'web_vital', {
                    name: 'LCP',
                    value: Math.round(lastEntry.startTime),
                    event_category: 'Performance'
                });
            }
        });
        
        observer.observe({ type: 'largest-contentful-paint', buffered: true });
    }
    
    // Monitor First Input Delay (FID)
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            
            entries.forEach(entry => {
                const fid = entry.processingStart - entry.startTime;
                console.log('FID:', fid);
                
                if (window.gtag) {
                    window.gtag('event', 'web_vital', {
                        name: 'FID',
                        value: Math.round(fid),
                        event_category: 'Performance'
                    });
                }
            });
        });
        
        observer.observe({ type: 'first-input', buffered: true });
    }
}

/**
 * Utility functions for external use
 */
export const optimization = {
    // Register custom scroll handler
    onScroll: (handler) => {
        scrollHandlers.push(handler);
    },
    
    // Register custom resize handler
    onResize: (handler) => {
        resizeHandlers.push(handler);
    },
    
    // Preload a resource
    preload: (url, as = 'fetch') => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        link.as = as;
        document.head.appendChild(link);
    },
    
    // Check if user prefers reduced motion
    prefersReducedMotion: () => {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    
    // Get connection information
    getConnectionInfo: () => {
        if ('connection' in navigator) {
            return {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt,
                saveData: navigator.connection.saveData
            };
        }
        return null;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { loadComponent, loadComponentOnView, optimization };
}

// Add CSS for lazy loading states
const style = document.createElement('style');
style.textContent = `
    .lazy {
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .lazy.loaded {
        opacity: 1;
    }
    
    .lazy.error {
        opacity: 0.5;
        filter: grayscale(100%);
    }
    
    [data-component].loading::after {
        content: '⏳';
        display: inline-block;
        margin-left: 8px;
    }
    
    [data-component].error {
        border: 1px solid #ff6b6b;
        background-color: rgba(255, 107, 107, 0.1);
        padding: 8px;
        border-radius: 4px;
    }
`;
document.head.appendChild(style);
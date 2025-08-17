import type { AppProps } from "next/app";
import Head from "next/head";
import { useEffect } from "react";
import "../styles.css";

// Performance monitoring
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

function reportWebVitals(metric: any) {
  // Log performance metrics
  if (process.env.NODE_ENV === 'production') {
    console.log('Performance metric:', metric);
    
    // Send to analytics if available
    if (window.gtag) {
      window.gtag('event', metric.name, {
        event_category: 'Web Vitals',
        event_label: metric.id,
        value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
        non_interaction: true,
      });
    }
  }
}

export default function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Register service worker for PWA capabilities
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      navigator.serviceWorker.register('/sw.js').catch((err) => {
        console.warn('Service worker registration failed:', err);
      });
    }

    // Performance observer for monitoring
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'navigation') {
            console.log('Navigation timing:', entry);
          } else if (entry.entryType === 'largest-contentful-paint') {
            console.log('LCP:', entry.startTime);
          } else if (entry.entryType === 'first-input') {
            const fidEntry = entry as any; // Type assertion for FID entry
            console.log('FID:', fidEntry.processingStart - fidEntry.startTime);
          }
        });
      });

      try {
        observer.observe({ entryTypes: ['navigation', 'largest-contentful-paint', 'first-input'] });
      } catch (e) {
        console.warn('Performance observer not supported:', e);
      }

      return () => observer.disconnect();
    }
  }, []);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0b0f16" />
        <meta name="description" content="Lyra AI - Your personality-driven AI console" />
        <meta property="og:title" content="Lyra AI Console" />
        <meta property="og:description" content="Your personality-driven AI console for intelligent assistance" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content="Lyra AI Console" />
        <meta name="twitter:description" content="Your personality-driven AI console for intelligent assistance" />
        
        {/* Preload critical resources */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* PWA meta tags */}
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
        
        {/* Prevent FOUC */}
        <style dangerouslySetInnerHTML={{
          __html: `
            html { background-color: #0b0f16; }
            body { visibility: hidden; }
            body.loaded { visibility: visible; }
          `
        }} />
      </Head>
      <Component {...pageProps} />
      
      <script
        dangerouslySetInnerHTML={{
          __html: `
            // Show body when page is loaded
            document.addEventListener('DOMContentLoaded', function() {
              document.body.classList.add('loaded');
            });
            
            // Error tracking
            window.addEventListener('error', function(e) {
              console.error('Global error:', e.error);
            });
            
            window.addEventListener('unhandledrejection', function(e) {
              console.error('Unhandled promise rejection:', e.reason);
            });
          `
        }}
      />
    </>
  );
}

export { reportWebVitals };

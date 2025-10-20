// Image Loading Optimization
// Handles lazy loading, error states, and performance

(function() {
    'use strict';
    
    // Add loaded class when image loads (for fade-in effect)
    function handleImageLoad() {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        
        lazyImages.forEach(img => {
            if (img.complete) {
                img.classList.add('loaded');
            } else {
                img.addEventListener('load', function() {
                    this.classList.add('loaded');
                }, { once: true, passive: true });
            }
            
            // Handle error state
            img.addEventListener('error', function() {
                this.style.display = 'none';
                const parent = this.parentElement;
                if (parent) {
                    parent.style.background = '#f0f0f0';
                    parent.style.display = 'flex';
                    parent.style.alignItems = 'center';
                    parent.style.justifyContent = 'center';
                    parent.innerHTML = '<i class="fas fa-image" style="font-size: 3rem; color: #ccc;"></i>';
                }
            }, { once: true, passive: true });
        });
    }
    
    // Progressive image loading for large images
    function addProgressiveLoading() {
        const largeImages = document.querySelectorAll('.blog-featured-image img, .hero-image img');
        
        largeImages.forEach(img => {
            // Add loading indicator
            const container = img.parentElement;
            if (container && !img.complete) {
                container.style.position = 'relative';
                container.style.background = 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)';
                container.style.backgroundSize = '200% 100%';
                container.style.animation = 'loading 1.5s ease-in-out infinite';
            }
            
            img.addEventListener('load', function() {
                if (container) {
                    container.style.background = 'none';
                    container.style.animation = 'none';
                }
            }, { once: true, passive: true });
        });
    }
    
    // Add loading animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        .responsive-img {
            max-width: 100%;
            height: auto;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            handleImageLoad();
            addProgressiveLoading();
        }, { passive: true });
    } else {
        handleImageLoad();
        addProgressiveLoading();
    }
    
    // Intersection Observer for better lazy loading control
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Preload next image when current comes into view
                    const nextImg = img.closest('article, .blog-post-card')?.nextElementSibling?.querySelector('img');
                    if (nextImg && nextImg.loading === 'lazy') {
                        // Trigger preload
                        const tempImg = new Image();
                        tempImg.src = nextImg.src;
                    }
                    
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px', // Start loading 50px before visible
            threshold: 0.01
        });
        
        // Observe all lazy images
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            imageObserver.observe(img);
        });
    }
})();


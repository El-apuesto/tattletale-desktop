// The Satire Chronicle - Main JavaScript

// Modal Functions
function showSubscribeModal() {
    document.getElementById('subscribeModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function hideSubscribeModal() {
    document.getElementById('subscribeModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('subscribeModal');
    if (event.target == modal) {
        hideSubscribeModal();
    }
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Header scroll effect
let lastScrollTop = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.boxShadow = 'none';
    }
    
    lastScrollTop = scrollTop;
});

// Newsletter form submission
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForms = document.querySelectorAll('.newsletter-form, .subscribe-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = form.querySelector('input[type="email"]').value;
            const button = form.querySelector('button');
            const originalText = button.textContent;
            
            // Show loading state
            button.textContent = 'Subscribing...';
            button.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                button.textContent = 'Subscribed!';
                button.style.background = 'var(--gold-accent)';
                
                // Reset form
                form.reset();
                
                // Hide modal if it's the subscribe modal
                if (form.closest('.modal-content')) {
                    setTimeout(() => {
                        hideSubscribeModal();
                        button.textContent = originalText;
                        button.style.background = '';
                        button.disabled = false;
                    }, 2000);
                } else {
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.background = '';
                        button.disabled = false;
                    }, 3000);
                }
            }, 1500);
        });
    });
});

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Article card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const articleCards = document.querySelectorAll('.article-card, .featured-card');
    
    articleCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Reading time estimation
function estimateReadingTime(text) {
    const wordsPerMinute = 200;
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(words / wordsPerMinute);
    return minutes;
}

// Add reading time to articles
document.addEventListener('DOMContentLoaded', function() {
    const articles = document.querySelectorAll('.article-content p');
    
    articles.forEach(article => {
        const text = article.textContent;
        const readingTime = estimateReadingTime(text);
        
        const readingTimeElement = document.createElement('span');
        readingTimeElement.className = 'reading-time';
        readingTimeElement.textContent = `${readingTime} min read`;
        readingTimeElement.style.fontSize = '0.875rem';
        readingTimeElement.style.color = 'var(--medium-gray)';
        readingTimeElement.style.marginLeft = 'var(--spacing-sm)';
        
        const metaElement = article.closest('.article-content, .featured-content').querySelector('.article-meta');
        if (metaElement) {
            metaElement.appendChild(readingTimeElement);
        }
    });
});

// Share functionality
function shareArticle(title, url, text) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            alert('Article link copied to clipboard!');
        }).catch(err => console.log('Error copying link:', err));
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Escape key closes modal
    if (e.key === 'Escape') {
        hideSubscribeModal();
    }
    
    // Ctrl/Cmd + K for search (if search is implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input if it exists
        const searchInput = document.querySelector('#search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Performance optimization - Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll events
const optimizedHeaderScroll = debounce(() => {
    // Header scroll logic here
}, 10);

window.addEventListener('scroll', optimizedHeaderScroll);

// Error handling for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            
            // Create placeholder
            const placeholder = document.createElement('div');
            placeholder.className = 'image-placeholder';
            placeholder.innerHTML = '<span class="placeholder-text">SC</span>';
            placeholder.style.cssText = `
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, var(--silver-accent) 0%, var(--light-gray) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--pure-white);
                font-family: var(--font-serif);
                font-size: 2rem;
                font-weight: 900;
            `;
            
            this.parentNode.appendChild(placeholder);
        });
    });
});

// Analytics and tracking (placeholder)
function trackEvent(eventName, properties = {}) {
    // Placeholder for analytics tracking
    console.log('Event tracked:', eventName, properties);
    
    // Example: Send to analytics service
    // gtag('event', eventName, properties);
}

// Track newsletter signups
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForms = document.querySelectorAll('.newsletter-form, .subscribe-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function() {
            trackEvent('newsletter_signup', {
                location: 'homepage'
            });
        });
    });
});

// Track article views
function trackArticleView(articleId) {
    trackEvent('article_view', {
        article_id: articleId
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('The Satire Chronicle - Loaded');
    
    // Add loading animation
    document.body.classList.add('loaded');
    
    // Track page view
    trackEvent('page_view', {
        page: window.location.pathname
    });
});

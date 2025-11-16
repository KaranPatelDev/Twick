// Twick Documentation Site - Interactive JavaScript

// Smooth scrolling and navigation
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initNavbar();
    initSearch();
    initCodeBlocks();
    initTabs();
    initTooltips();
    initScrollSpy();
    
    // Smooth scroll for anchor links
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
});

// Navbar scroll effect
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput) return;
    
    let searchData = [];
    
    // Load search data
    loadSearchData();
    
    searchInput.addEventListener('input', debounce(performSearch, 300));
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    function loadSearchData() {
        // Extract searchable content from the page
        const sections = document.querySelectorAll('section[id], .card, .code-block');
        sections.forEach(section => {
            const title = section.querySelector('h1, h2, h3, h4, h5, h6')?.textContent || '';
            const content = section.textContent || '';
            const id = section.id || '';
            
            if (title && content) {
                searchData.push({
                    title: title.trim(),
                    content: content.trim(),
                    url: id ? `#${id}` : '#',
                    section: section
                });
            }
        });
    }
    
    function performSearch() {
        const query = searchInput.value.toLowerCase().trim();
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        const results = searchData.filter(item => 
            item.title.toLowerCase().includes(query) ||
            item.content.toLowerCase().includes(query)
        ).slice(0, 10);
        
        displaySearchResults(results, query);
    }
    
    function displaySearchResults(results, query) {
        if (!searchResults) return;
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            const resultsHTML = results.map(result => `
                <div class="search-result-item" onclick="navigateToResult('${result.url}')">
                    <h5>${highlightQuery(result.title, query)}</h5>
                    <p>${highlightQuery(truncateText(result.content, 150), query)}</p>
                </div>
            `).join('');
            
            searchResults.innerHTML = resultsHTML;
        }
        
        searchResults.style.display = 'block';
    }
    
    function hideSearchResults() {
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }
    
    function highlightQuery(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    function truncateText(text, length) {
        return text.length > length ? text.substring(0, length) + '...' : text;
    }
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults?.contains(e.target)) {
            hideSearchResults();
        }
    });
}

// Navigate to search result
function navigateToResult(url) {
    if (url && url !== '#') {
        const target = document.querySelector(url);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
            // Hide search results
            const searchResults = document.getElementById('searchResults');
            if (searchResults) {
                searchResults.style.display = 'none';
            }
        }
    }
}

// Code block functionality
function initCodeBlocks() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const codeBlock = this.closest('.code-block');
            const codeContent = codeBlock.querySelector('.code-content, code, pre');
            
            if (codeContent) {
                copyToClipboard(codeContent.textContent);
                showCopyFeedback(this);
            }
        });
    });
}

// Enhanced copy-to-clipboard functionality with better UX
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showCopySuccess();
    }).catch(function(err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showCopySuccess();
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showCopyError();
        }
        document.body.removeChild(textArea);
    });
}

// Show success toast notification
function showCopySuccess() {
    const toast = createToast('✓ Copied to clipboard!', 'success');
    showToast(toast);
}

// Show error toast notification
function showCopyError() {
    const toast = createToast('❌ Failed to copy', 'error');
    showToast(toast);
}

// Create toast element
function createToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'x-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style based on type
    if (type === 'error') {
        toast.style.background = '#dc3545';
    }
    
    return toast;
}

// Show toast notification
function showToast(toast) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Trigger show animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Enhanced button feedback for copy actions
function initCopyButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.copy-btn, .copy-cmd-btn')) {
            const button = e.target.closest('.copy-btn, .copy-cmd-btn');
            
            // Visual feedback
            button.classList.add('copied');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check"></i> Copied!';
            
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = originalText;
            }, 2000);
        }
    });
}

// Initialize enhanced copy functionality
document.addEventListener('DOMContentLoaded', function() {
    initCopyButtons();
});

// Utility function to convert traditional code blocks to enhanced cards
function enhanceCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        if (pre.tagName.toLowerCase() === 'pre' && !pre.closest('.command-card, .code-card')) {
            const language = block.className.replace('language-', '') || 'bash';
            const code = block.textContent;
            
            // Create enhanced command card
            const commandCard = document.createElement('div');
            commandCard.className = 'command-card';
            commandCard.innerHTML = `
                <div class="command-header">
                    <i class="bi bi-terminal"></i>
                    <span>${language.charAt(0).toUpperCase() + language.slice(1)}</span>
                    <button class="copy-btn" onclick="copyToClipboard(\`${code.replace(/`/g, '\\`')}\`)" title="Copy to clipboard">
                        <i class="bi bi-clipboard"></i>
                        Copy
                    </button>
                </div>
                <div class="command-body">
                    <code>${code.replace(/\n/g, '<br>')}</code>
                </div>
            `;
            
            // Replace the original pre element
            pre.parentNode.replaceChild(commandCard, pre);
        }
    });
}

// Auto-enhance code blocks on page load
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure all content is loaded
    setTimeout(enhanceCodeBlocks, 100);
});

// Dark mode toggle (if implemented)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});

// Performance monitoring
function logPerformance() {
    if (window.performance) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
}

window.addEventListener('load', logPerformance);

// Export functions for external use
window.TwickDocs = {
    navigateToResult,
    toggleDarkMode,
    copyToClipboard,
    showLoading,
    hideLoading
};

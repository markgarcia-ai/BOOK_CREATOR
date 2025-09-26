// Book Creator Frontend Application
class BookCreatorApp {
    constructor() {
        this.bookTypes = {};
        this.selectedBookType = null;
        this.init();
    }

    async init() {
        // Initialize Lucide icons
        lucide.createIcons();

        // Set up event listeners
        this.setupEventListeners();

        // Load initial data
        await this.loadBookTypes();
        await this.checkSystemStatus();

        // Initialize form
        this.updateEstimates();
    }

    setupEventListeners() {
        // Navigation
        const navToggle = document.getElementById('navToggle');
        if (navToggle) navToggle.addEventListener('click', this.toggleMobileNav);
        
        // Form elements
        const form = document.getElementById('bookForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        // Form inputs for real-time updates
        ['bookType', 'chapters', 'wordsPerChapter'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', this.updateEstimates.bind(this));
                element.addEventListener('input', this.updateEstimates.bind(this));
            }
        });

        // Book type selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.book-type-card')) {
                this.selectBookType(e.target.closest('.book-type-card'));
            }
        });

        // File upload
        const fileInput = document.getElementById('sourceFile');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileUpload.bind(this));
        }
    }

    async loadBookTypes() {
        try {
            const response = await fetch('/api/book-types');
            this.bookTypes = await response.json();
            this.renderBookTypes();
            this.populateBookTypeSelect();
        } catch (error) {
            console.error('Failed to load book types:', error);
            this.showNotification('Failed to load book types', 'error');
        }
    }

    renderBookTypes() {
        const container = document.getElementById('bookTypesGrid');
        if (!container) return;

        container.innerHTML = Object.entries(this.bookTypes).map(([key, type]) => `
            <div class="book-type-card" data-type="${key}">
                <div class="book-type-header">
                    <div>
                        <div class="book-type-name">${type.name}</div>
                        <div class="book-type-audience">${type.target_audience}</div>
                    </div>
                    <div class="book-type-cost">$${type.estimated_cost_usd.toFixed(3)}</div>
                </div>
                <div class="book-type-description">${type.description}</div>
                <div class="book-type-specs">
                    <div class="spec-item">
                        <span class="spec-label">Chapters:</span>
                        <span class="spec-value">${type.recommended_chapters}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Words/Chapter:</span>
                        <span class="spec-value">${type.words_per_chapter.toLocaleString()}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Pages:</span>
                        <span class="spec-value">~${type.estimated_pages}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-label">Time:</span>
                        <span class="spec-value">${this.formatTime(type.estimated_time_minutes)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populateBookTypeSelect() {
        const select = document.getElementById('bookType');
        if (!select) return;

        // Clear existing options except the first one
        select.innerHTML = '<option value="">Select book type...</option>';

        Object.entries(this.bookTypes).forEach(([key, type]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = type.name;
            select.appendChild(option);
        });
    }

    selectBookType(card) {
        // Remove previous selection
        document.querySelectorAll('.book-type-card').forEach(c => c.classList.remove('selected'));
        
        // Add selection to clicked card
        card.classList.add('selected');
        
        // Update form
        const typeKey = card.dataset.type;
        const select = document.getElementById('bookType');
        if (select) {
            select.value = typeKey;
        }

        // Update form fields with book type defaults
        const bookType = this.bookTypes[typeKey];
        if (bookType) {
            const chaptersInput = document.getElementById('chapters');
            const wordsInput = document.getElementById('wordsPerChapter');
            
            if (chaptersInput && chaptersInput.value == chaptersInput.defaultValue) {
                chaptersInput.value = bookType.recommended_chapters;
            }
            
            if (wordsInput && wordsInput.value == wordsInput.defaultValue) {
                wordsInput.value = bookType.words_per_chapter;
            }
        }

        this.selectedBookType = typeKey;
        this.updateEstimates();

        // Scroll to generator
        const generator = document.getElementById('generator');
        if (generator) generator.scrollIntoView({ behavior: 'smooth' });
    }

    updateEstimates() {
        const bookTypeEl = document.getElementById('bookType');
        const chaptersEl = document.getElementById('chapters');
        const wordsPerChapterEl = document.getElementById('wordsPerChapter');
        
        const bookType = bookTypeEl ? bookTypeEl.value : '';
        const chapters = parseInt((chaptersEl ? chaptersEl.value : '') || 0);
        const wordsPerChapter = parseInt((wordsPerChapterEl ? wordsPerChapterEl.value : '') || 0);

        if (!chapters || !wordsPerChapter) {
            this.setEstimate('estimatedPages', '0');
            this.setEstimate('estimatedTime', '0 min');
            this.setEstimate('estimatedCost', '$0.00');
            return;
        }

        const totalWords = chapters * wordsPerChapter;
        const estimatedPages = Math.ceil(totalWords / 250);
        
        // Calculate time and cost based on book type or defaults
        let timeMinutes = Math.ceil(chapters * 3 + (totalWords / 1000) * 0.8);
        let cost = 0.002 * (totalWords / 1000) * 1.5; // Base calculation

        if (bookType && this.bookTypes[bookType]) {
            const typeData = this.bookTypes[bookType];
            const ratio = totalWords / (typeData.recommended_chapters * typeData.words_per_chapter);
            timeMinutes = Math.ceil(typeData.estimated_time_minutes * ratio);
            cost = typeData.estimated_cost_usd * ratio;
        }

        this.setEstimate('estimatedPages', estimatedPages.toString());
        this.setEstimate('estimatedTime', this.formatTime(timeMinutes));
        this.setEstimate('estimatedCost', `$${cost.toFixed(3)}`);
    }

    setEstimate(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatTime(minutes) {
        if (minutes < 60) {
            return `${minutes}m`;
        } else if (minutes < 120) {
            const hours = (minutes / 60).toFixed(1);
            return `${hours}h`;
        } else {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return mins === 0 ? `${hours}h` : `${hours}h ${mins}m`;
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            topic: formData.get('title'),
            book_type: formData.get('bookType'),
            chapters: parseInt(formData.get('chapters')),
            words_per_chapter: parseInt(formData.get('wordsPerChapter'))
        };

        // Add book type info if selected
        if (data.book_type && this.bookTypes[data.book_type]) {
            const bookType = this.bookTypes[data.book_type];
            data.book_type_info = {
                name: bookType.name,
                target_audience: bookType.target_audience,
                writing_style: "Specialized for " + bookType.name.toLowerCase(),
                content_approach: bookType.description,
                tone_description: "Professional and targeted",
                section_emphasis: ["High-quality content", "Structured approach"],
                prompt_modifiers: {
                    structure: "Organize content according to " + bookType.name + " standards",
                    depth: "Provide appropriate depth for " + bookType.target_audience,
                    examples: "Include relevant examples for " + bookType.target_audience
                }
            };
        }

        // Handle file upload
        const fileInput = document.getElementById('sourceFile');
        if (fileInput.files.length > 0) {
            try {
                const file = fileInput.files[0];
                const fileName = file.name.toLowerCase();
                
                if (fileName.endsWith('.html') || fileName.endsWith('.htm') || fileName.endsWith('.zip')) {
                    // Process HTML/ZIP file through special endpoint
                    this.showProgress('Processing HTML file...', 10);
                    const htmlProcessResult = await this.processHTMLFile(file);
                    if (htmlProcessResult && htmlProcessResult.success) {
                        data.source_content = htmlProcessResult.markdown_content;
                        this.showNotification(`HTML processed: ${htmlProcessResult.processing_result.word_count} words, ${htmlProcessResult.processing_result.images_count} images`, 'success');
                    } else {
                        this.showNotification('Failed to process HTML file', 'error');
                        return;
                    }
                } else {
                    // Handle regular markdown/text files
                    data.source_content = await this.readFileAsText(file);
                }
            } catch (error) {
                this.showNotification('Failed to read uploaded file', 'error');
                return;
            }
        }

        await this.generateBook(data);
    }

    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    async processHTMLFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload-html', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error processing HTML file:', error);
            throw error;
        }
    }

    async generateBook(data) {
        const form = document.getElementById('bookForm');
        const progress = document.getElementById('generationProgress');
        const results = document.getElementById('generationResults');

        // Show progress
        form.style.display = 'none';
        progress.style.display = 'block';
        results.style.display = 'none';

        this.updateProgress(0, 'Initializing book generation...');

        try {
            // Simulate progress updates
            const progressSteps = [
                { percent: 10, message: 'Analyzing book requirements...' },
                { percent: 25, message: 'Creating book structure...' },
                { percent: 40, message: 'Generating chapter content...' },
                { percent: 70, message: 'Enhancing content quality...' },
                { percent: 85, message: 'Formatting and styling...' },
                { percent: 95, message: 'Finalizing book...' }
            ];

            let stepIndex = 0;
            const progressInterval = setInterval(() => {
                if (stepIndex < progressSteps.length) {
                    const step = progressSteps[stepIndex];
                    this.updateProgress(step.percent, step.message);
                    stepIndex++;
                }
            }, 2000);

            const response = await fetch('/api/generate-book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Generation failed');
            }

            const result = await response.json();
            this.updateProgress(100, 'Book generation completed!');

            setTimeout(() => {
                this.showResults(result);
                progress.style.display = 'none';
                results.style.display = 'block';
            }, 1000);

        } catch (error) {
            console.error('Generation error:', error);
            this.showNotification(`Generation failed: ${error.message}`, 'error');
            
            // Reset form
            form.style.display = 'block';
            progress.style.display = 'none';
        }
    }

    updateProgress(percent, message) {
        const fill = document.getElementById('progressFill');
        const status = document.getElementById('progressStatus');
        const details = document.getElementById('progressDetails');

        if (fill) fill.style.width = `${percent}%`;
        if (status) status.textContent = message;
        
        if (details) {
            details.innerHTML = `
                <div>Progress: ${percent}%</div>
                <div>${message}</div>
            `;
        }
    }

    showResults(result) {
        const container = document.getElementById('generationResults');
        if (!container) return;

        const stats = (result.result && result.result.statistics) || {};
        const files = (result.result && result.result.files) || {};

        container.innerHTML = `
            <div class="results-header">
                <h3>✅ Book Generated Successfully!</h3>
                <p>Your book "${(result.result && result.result.topic) || 'Untitled'}" has been created.</p>
            </div>
            
            <div class="results-grid">
                <div class="result-card">
                    <div class="result-value">${stats.total_chapters || 0}</div>
                    <div class="result-label">Chapters</div>
                </div>
                <div class="result-card">
                    <div class="result-value">${(stats.total_words || 0).toLocaleString()}</div>
                    <div class="result-label">Words</div>
                </div>
                <div class="result-card">
                    <div class="result-value">${stats.estimated_pages || 0}</div>
                    <div class="result-label">Pages</div>
                </div>
                <div class="result-card">
                    <div class="result-value">$${(stats.total_cost || 0).toFixed(3)}</div>
                    <div class="result-label">Cost</div>
                </div>
            </div>

            <div class="download-links">
                ${files.markdown ? `<a href="${files.markdown}" class="download-link" target="_blank"><i data-lucide="file-text"></i> Markdown</a>` : ''}
                ${files.html ? `<a href="${files.html}" class="download-link" target="_blank"><i data-lucide="globe"></i> HTML</a>` : ''}
                ${files.report ? `<a href="${files.report}" class="download-link" target="_blank"><i data-lucide="bar-chart"></i> Report</a>` : ''}
                ${Object.keys(files.styles || {}).map(style => 
                    `<a href="${files.styles[style]}" class="download-link" target="_blank"><i data-lucide="palette"></i> ${style.charAt(0).toUpperCase() + style.slice(1)}</a>`
                ).join('')}
            </div>

            <div style="margin-top: 2rem; text-align: center;">
                <button class="btn btn-primary" onclick="location.reload()">
                    <i data-lucide="plus"></i>
                    Create Another Book
                </button>
            </div>
        `;

        // Re-initialize icons for new content
        lucide.createIcons();
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const indicator = document.getElementById('systemStatus');
            const details = document.getElementById('statusDetails');
            
            if (data.backend && data.backend.status === 'healthy') {
                indicator.innerHTML = '<i data-lucide="check-circle"></i> Healthy';
                indicator.className = 'status-indicator healthy';
                
                if (details) {
                    details.innerHTML = `
                        <div>✅ Frontend: ${data.frontend}</div>
                        <div>✅ Backend: ${data.backend.status}</div>
                        <div>🔧 Version: ${data.backend.version || 'Unknown'}</div>
                        <div>📡 Features: ${Object.entries(data.backend.features || {})
                            .filter(([, enabled]) => enabled)
                            .map(([feature]) => feature.replace('_', ' '))
                            .join(', ') || 'None'}</div>
                    `;
                }
            } else {
                indicator.innerHTML = '<i data-lucide="x-circle"></i> Unhealthy';
                indicator.className = 'status-indicator unhealthy';
                
                if (details) {
                    details.innerHTML = `
                        <div>⚠️ Backend connection failed</div>
                        <div>Some features may not be available</div>
                    `;
                }
            }
        } catch (error) {
            console.error('Status check failed:', error);
            const indicator = document.getElementById('systemStatus');
            const details = document.getElementById('statusDetails');
            
            if (indicator) {
                indicator.innerHTML = '<i data-lucide="alert-triangle"></i> Error';
                indicator.className = 'status-indicator unhealthy';
            }
            
            if (details) {
                details.innerHTML = `
                    <div>❌ System status check failed</div>
                    <div>Please try refreshing the page</div>
                `;
            }
        }

        // Re-initialize icons
        lucide.createIcons();
    }

    handleFileUpload(e) {
        const file = e.target.files[0];
        const uploadContent = document.querySelector('.file-upload-content');
        
        if (file && uploadContent) {
            uploadContent.innerHTML = `
                <i data-lucide="file-check"></i>
                <span>Selected: ${file.name}</span>
                <small>(${this.formatFileSize(file.size)})</small>
            `;
            lucide.createIcons();
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    toggleMobileNav() {
        // Implement mobile navigation toggle if needed
        console.log('Mobile nav toggle');
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? 'var(--danger)' : 'var(--primary)'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            max-width: 400px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Utility functions
function scrollToGenerator() {
    const generator = document.getElementById('generator');
    if (generator) generator.scrollIntoView({ behavior: 'smooth' });
}

function scrollToBookTypes() {
    const bookTypes = document.getElementById('book-types');
    if (bookTypes) bookTypes.scrollIntoView({ behavior: 'smooth' });
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BookCreatorApp();
});

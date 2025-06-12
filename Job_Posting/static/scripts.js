// Complete Job Posting Generator - Files API Client JavaScript
console.log('Job Posting Generator scripts loaded');

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const jobForm = document.getElementById('job-form');
    const jobTitleInput = document.getElementById('job-title');
    const locationInput = document.getElementById('location');
    // Company name, location, industry are now managed via Settings modal
    // Form fields for job posting details
    const experienceInput = document.getElementById('experience-level');
    const employmentTypeInput = document.getElementById('employment-type');
    const keywordsInput = document.getElementById('keywords');
    const modelSelect = document.getElementById('model-select');
    const lengthInput = document.getElementById('length');
    const jobOverviewInput = document.getElementById('job-overview');
    // Responsibilities input as multiline textarea
    const responsibilitiesTextarea = document.getElementById('responsibilities');
    const teamIntroInput = document.getElementById('team-intro');
    const requiredSkillsInput = document.getElementById('required-skills');
    const educationRequirementsInput = document.getElementById('education-requirements');
    const experienceDetailsInput = document.getElementById('experience-details');
    const certificationsInput = document.getElementById('certifications');
    const salaryToggleInput = document.getElementById('include-salary');
    const salaryRangeInput = document.getElementById('salary-range');
    const benefitCheckboxes = document.querySelectorAll('.benefit-checkbox');
    const perksInput = document.getElementById('perks');
    const applicationDeadlineInput = document.getElementById('application-deadline');
    const applicationDeadlineDateInput = document.getElementById('application-deadline-date');
    // Toggle between days and date for application deadline, with initial state
    if (applicationDeadlineInput && applicationDeadlineDateInput) {
        applicationDeadlineInput.addEventListener('input', () => {
            if (applicationDeadlineInput.value) {
                applicationDeadlineDateInput.disabled = true;
                applicationDeadlineDateInput.value = '';
            } else {
                applicationDeadlineDateInput.disabled = false;
            }
        });
        applicationDeadlineDateInput.addEventListener('change', () => {
            if (applicationDeadlineDateInput.value) {
                applicationDeadlineInput.disabled = true;
                applicationDeadlineInput.value = '';
            } else {
                applicationDeadlineInput.disabled = false;
            }
        });
    }
    const generateButton = document.getElementById('generate-button');
    const copyButton = document.getElementById('copy-button');
    const downloadButton = document.getElementById('download-button');
    const downloadDocxBtn = document.getElementById('download-docx');
    const downloadPdfBtn = document.getElementById('download-pdf');
    const exportGdocsBtn = document.getElementById('export-gdocs');
    const loadingIndicator = document.getElementById('loading-indicator');
    const emptyState = document.getElementById('empty-state');
    const generatedContent = document.getElementById('generated-content');
    const jobResult = document.getElementById('job-result');
    const toggleThemeBtn = document.getElementById('toggle-theme');
    const errorNotification = document.getElementById('error-notification');
    const errorMessage = document.getElementById('error-message');

    // Initialize theme
    function initTheme() {
        const isDark = localStorage.getItem('darkMode') === 'true';
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
        // Sync Tailwind dark class for dark: variants
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        updateThemeIcon(isDark);
        
        // Set default model if no selection
        if (modelSelect && !modelSelect.value) {
            modelSelect.value = "claude-opus-4-20250514";
        }
    }

    function updateThemeIcon(isDark) {
        if (toggleThemeBtn && toggleThemeBtn.querySelector('svg')) {
            toggleThemeBtn.querySelector('svg').innerHTML = isDark
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>';
        }
    }

    // Theme handler
    if (toggleThemeBtn) {
        toggleThemeBtn.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            const newMode = isDark ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newMode);
            // Toggle Tailwind dark class as well
            if (newMode === 'dark') document.documentElement.classList.add('dark'); else document.documentElement.classList.remove('dark');
            localStorage.setItem('darkMode', newMode === 'dark');
            updateThemeIcon(newMode === 'dark');
        });
    }

    // Files API status check removed per user request

    // Markdown content formatting
    function formatContent(content) {
        if (typeof marked !== 'undefined') {
            // Pre-process content to ensure proper line breaks for bullet points
            let processedContent = content
                // Ensure bullet points have proper line breaks
                .replace(/([.!?])\s*([•\-\*])/g, '$1\n\n$2')
                // Ensure double line breaks before headers
                .replace(/([.!?])\s*(#{1,6}\s)/g, '$1\n\n$2')
                // Fix bullet points that might be missing spaces
                .replace(/^([•\-\*])([^\s])/gm, '$1 $2')
                // Ensure proper spacing around bullet points
                .replace(/\n([•\-\*])/g, '\n\n$1');

            let formattedContent = marked.parse(processedContent);

            // Improve formatting of generated HTML
            formattedContent = formattedContent
                .replace(/<ul>/g, '<ul class="list-disc pl-5 my-2">')
                .replace(/<ol>/g, '<ol class="list-decimal pl-5 my-2">')
                .replace(/<li>\s*<p>/g, '<li>')
                .replace(/<\/p>\s*<\/li>/g, '</li>')
                .replace(/<h1/g, '<h1 class="text-2xl font-bold mt-4 mb-2"')
                .replace(/<h2/g, '<h2 class="text-xl font-semibold mt-3 mb-2"')
                .replace(/<h3/g, '<h3 class="text-lg font-medium mt-3 mb-1"')
                .replace(/<p>/g, '<p class="my-2">')
                .replace(/<strong>/g, '<strong class="font-semibold">')
                .replace(/<blockquote>/g, '<blockquote class="border-l-4 border-gray-300 pl-4 my-3 text-gray-600 dark:text-gray-400 italic">')
                .replace(/>\s+</g, '><')
                .replace(/\n\s*\n/g, '\n');

            return formattedContent;
        }
        
        // Fallback: enhanced line break formatting with bullet points
        return content
            .replace(/\n/g, '<br>')
            .replace(/([•\-\*])\s*([^<])/g, '<br>$1 $2')
            .replace(/(<br>)+/g, '<br>');
    }

    // Function to analyze job description content
    async function analyzeJobDescription(content) {
        if (!content || content.length < 50) return null;
        
        try {
            const response = await fetch('/api/analyze/job-description', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_description: content,
                    job_title: jobTitleInput.value.trim(),
                    company_name: document.getElementById('company-name')?.value || ''
                })
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Analysis error:', error);
        }
        return null;
    }
    
    // Function to show content analysis hint (discrete)
    function showAnalysisHint(analysisResult) {
        const hintElement = document.getElementById('content-analysis-hint');
        const textElement = document.getElementById('analysis-text');
        
        if (!analysisResult || !hintElement || !textElement) return;
        
        // Clean messages without technical details
        const discreteMessages = {
            'scenario_a': '🎯 Complete content detected - ready for optimization!',
            'scenario_b': '📝 Perfect for detailed job posting creation',
            'scenario_c': '⚡ Great! I\'ll enhance your content with additional details'
        };
        
        const message = discreteMessages[analysisResult.mode] || 'Content analyzed - optimizing approach';
        textElement.textContent = message;
        hintElement.classList.remove('hidden');
        
        // Show complete content guide if applicable
        if (analysisResult.mode === 'scenario_a') {
            showCompleteContentGuide();
        }
        
        // Auto-hide hint after 3 seconds
        setTimeout(() => {
            hintElement.classList.add('hidden');
        }, 3000);
    }
    
    // Smart Scenario A Guide Functions
    function showCompleteContentGuide() {
        const guide = document.getElementById('scenario-a-guide');
        const smartHintTrigger = document.getElementById('smart-hint-trigger');
        
        if (guide) {
            guide.classList.remove('hidden');
            // Auto-hide after 8 seconds unless user interacts
            setTimeout(() => {
                if (!guide.classList.contains('hidden')) {
                    guide.classList.add('hidden');
                    smartHintTrigger?.classList.remove('hidden'); // Show the trigger for later
                }
            }, 8000);
        }
    }
    
    function hideCompleteContentGuide() {
        const guide = document.getElementById('scenario-a-guide');
        const smartHintTrigger = document.getElementById('smart-hint-trigger');
        
        if (guide) {
            guide.classList.add('hidden');
            smartHintTrigger?.classList.remove('hidden'); // Show trigger for future use
        }
    }
    
    function showCompleteContentHint() {
        showCompleteContentGuide();
    }
    
    // Smart clipboard detection
    function detectLargeClipboardContent() {
        const jobOverview = document.getElementById('job-overview');
        
        jobOverview?.addEventListener('focus', async () => {
            try {
                const text = await navigator.clipboard.readText();
                if (text.length > 800 && looksLikeJobDescription(text)) {
                    showQuickClipboardHint(text.length);
                }
            } catch (err) {
                // Clipboard access not available - silent fallback
            }
        });
    }
    
    function looksLikeJobDescription(text) {
        const indicators = [
            /job description|position|role/i,
            /responsibilities|duties/i,
            /requirements|qualifications/i,
            /experience|skills/i,
            /benefits|salary/i
        ];
        
        return indicators.filter(pattern => pattern.test(text)).length >= 3;
    }
    
    function showQuickClipboardHint(length) {
        const hint = document.createElement('div');
        hint.className = 'fixed top-4 right-4 max-w-sm p-3 bg-blue-100 border border-blue-300 text-blue-800 rounded-lg shadow-lg z-50';
        hint.innerHTML = `
            <div class="flex items-start space-x-2">
                <span class="text-lg">📋</span>
                <div class="flex-1">
                    <p class="text-sm font-medium">Large content detected in clipboard!</p>
                    <p class="text-xs mt-1">Detected ${length} characters. This looks like a complete job description - perfect for quick enhancement!</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="text-blue-600 hover:text-blue-800 ml-2">✕</button>
            </div>
        `;
        
        document.body.appendChild(hint);
        
        // Auto-remove after 6 seconds
        setTimeout(() => {
            if (hint.parentElement) {
                hint.remove();
            }
        }, 6000);
    }
    
    // Initialize smart features
    function initializeSmartFeatures() {
        // Initialize clipboard detection
        detectLargeClipboardContent();
        
        // Add intelligent content analysis to job overview field
        let analysisTimeout;
        if (jobOverviewInput) {
            jobOverviewInput.addEventListener('input', function() {
                clearTimeout(analysisTimeout);
                const content = this.value.trim();
                
                // Hide hints if content is too short
                if (content.length < 50) {
                    document.getElementById('content-analysis-hint')?.classList.add('hidden');
                    document.getElementById('scenario-a-guide')?.classList.add('hidden');
                    return;
                }
                
                // Debounce analysis to avoid too many requests
                analysisTimeout = setTimeout(async () => {
                    const analysis = await analyzeJobDescription(content);
                    if (analysis) {
                        showAnalysisHint(analysis);
                    }
                }, 1000);
            });
            
            // Smart paste detection on paste event
            jobOverviewInput.addEventListener('paste', function(e) {
                setTimeout(() => {
                    const content = this.value.trim();
                    if (content.length > 800) {
                        // Immediate analysis for large pastes
                        analyzeJobDescription(content).then(analysis => {
                            if (analysis && analysis.mode === 'scenario_a') {
                                showCompleteContentGuide();
                            }
                        });
                    }
                }, 100);
            });
        }
    }
    
    // Initialize smart features
    initializeSmartFeatures();

    // Token stats display function removed per user request

    // Function to generate job posting
    async function generateJobPosting(event) {
        event.preventDefault();
        
        // Get form values
        const jobTitle = jobTitleInput.value.trim();
        if (!jobTitle) {
            showError('Please enter a job title');
            return;
        }
        
        // Store original values for restoration in case of error
        const platformInput = document.getElementById('platform');
        const lengthInput = document.getElementById('length');
        const originalValues = {
            jobTitle: jobTitleInput.value,
            experience: experienceInput.value,
            employmentType: employmentTypeInput.value,
            keywords: keywordsInput.value,
            platform: platformInput.value,
            length: lengthInput.value
        };
        
        // Begin generating
        loadingIndicator.classList.remove('hidden');
        emptyState.classList.add('hidden');
        generatedContent.classList.add('hidden');
        copyButton.disabled = true;
        downloadButton.disabled = true;
        if (downloadDocxBtn) downloadDocxBtn.disabled = true;
        if (downloadPdfBtn) downloadPdfBtn.disabled = true;
        if (exportGdocsBtn) exportGdocsBtn.disabled = true;
        generateButton.disabled = true;
        
        try {
            console.log("Starting job posting generation for:", jobTitle);
            
            // Build job posting request
            // Collect form values
            const experienceLevel = experienceInput.value;
            const employmentType = employmentTypeInput.value;
            const location = locationInput.value.trim();
            const overview = jobOverviewInput.value.trim();
            // Parse responsibilities from multiline textarea (with safety check)
            const responsibilities = responsibilitiesTextarea && responsibilitiesTextarea.value
                ? responsibilitiesTextarea.value
                      .split('\n')
                      .map(line => line.trim())
                      .filter(Boolean)
                : [];
            const teamIntro = teamIntroInput ? teamIntroInput.value.trim() : '';
            const requiredSkills = requiredSkillsInput ? requiredSkillsInput.value.trim() : '';
            const educationRequirements = educationRequirementsInput ? educationRequirementsInput.value.trim() : '';
            const experienceDetails = experienceDetailsInput ? experienceDetailsInput.value.trim() : '';
            const certifications = certificationsInput ? certificationsInput.value.trim() : '';
            const includeSalary = salaryToggleInput ? salaryToggleInput.checked : false;
            const salaryRange = salaryRangeInput ? salaryRangeInput.value.trim() : '';
            const benefits = benefitCheckboxes.length > 0 
                ? Array.from(benefitCheckboxes)
                    .filter(cb => cb.checked)
                    .map(cb => cb.value)
                : [];
            const perks = perksInput ? perksInput.value.trim() : '';
            const publicationPlatform = platformInput ? platformInput.value.trim() : 'LinkedIn';
            const lengthOption = lengthInput ? lengthInput.value : 'standard';
            const applicationDeadline = applicationDeadlineInput && applicationDeadlineInput.value
                ? parseInt(applicationDeadlineInput.value, 10)
                : null;
            const applicationDeadlineDate = applicationDeadlineDateInput ? applicationDeadlineDateInput.value || null : null;
            const keywords = keywordsInput ? keywordsInput.value.trim() : '';
            
            // Build request payload with intelligent enhancement support
            const payload = {
                job_title: jobTitle,
                job_description: overview,  // Primary field for intelligent analysis
                job_overview: overview,     // Keep for backward compatibility
                location,
                experience_level: experienceLevel,
                employment_type: employmentType,
                responsibilities,
                team_intro: teamIntro,
                required_skills: requiredSkills,
                education_requirements: educationRequirements,
                experience_details: experienceDetails,
                certifications,
                include_salary: includeSalary,
                salary_range: salaryRange,
                benefits,
                perks,
                platform: publicationPlatform,
                length: lengthOption,
                application_deadline: applicationDeadline,
                application_deadline_date: applicationDeadlineDate,
                keywords
            };
            
            // Make streaming request to Files API endpoint
            const response = await fetch('/api/generate/job-posting', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP Error: ${response.status}`);
            }
            
            // Prepare streaming reader
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let partial = '';
            
            // Reset display and show generated content area
            jobResult.innerHTML = '';
            generatedContent.classList.remove('hidden');
            
            // Read stream progressively
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                partial += decoder.decode(value, { stream: true });
                jobResult.innerHTML = formatContent(partial);
            }
            
            reader.releaseLock();
            
            // Enable action buttons after streaming completes
            copyButton.disabled = false;
            downloadButton.disabled = false;
            if (downloadDocxBtn) downloadDocxBtn.disabled = false;
            if (downloadPdfBtn) downloadPdfBtn.disabled = false;
            if (exportGdocsBtn) exportGdocsBtn.disabled = false;
            
            // Hide loading indicator after streaming completes
            loadingIndicator.classList.add('hidden');
            
            // Token stats display removed per user request
            
            // Add syntax highlighting now that full content is rendered
            if (typeof hljs !== 'undefined') {
                jobResult.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
            }
            
            // Preview enhancements: score & suggestions via analysis API
            const scoreEl = document.getElementById('quality-score');
            const barEl = document.getElementById('quality-bar');
            const suggEl = document.getElementById('suggestions');
            const spinner = document.getElementById('score-spinner');
            if (spinner) spinner.classList.remove('hidden');
            if (scoreEl && barEl && suggEl) {
                try {
                    // Determine selected model (fallback to null to use server default)
                    const selectedModel = modelSelect ? modelSelect.value : null;
                    const analyzeResp = await fetch('/api/analyze/job-posting', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ posting: jobResult.innerText, selected_model: selectedModel })
                    });
                    if (analyzeResp.ok) {
                        const { score, suggestions } = await analyzeResp.json();
                        scoreEl.textContent = `${score}%`;
                        barEl.style.width = `${score}%`;
                        // Show suggestions only if score < 90
                        if (score < 90 && suggestions.length) {
                            window.currentSuggestions = suggestions;
                            suggEl.innerHTML = `
                                <ul class="list-disc pl-5 mb-2">
                                    ${suggestions.map(s => `<li>${s}</li>`).join('')}
                                </ul>
                                <button id="open-suggestions" class="px-3 py-1 bg-green-500 text-white rounded text-sm">Apply Suggestions</button>
                            `;
                            setTimeout(() => {
                                const openBtn = document.getElementById('open-suggestions');
                                if (openBtn) {
                                    openBtn.addEventListener('click', () => {
                                        const listDiv = document.getElementById('suggestions-list');
                                        const commentInput = document.getElementById('suggestion-comment');
                                        const modal = document.getElementById('suggestions-modal');
                                        if (listDiv) {
                                            listDiv.innerHTML = window.currentSuggestions.map(s => `<p>• ${s}</p>`).join('');
                                        }
                                        if (commentInput) commentInput.value = '';
                                        if (modal) modal.classList.remove('hidden');
                                    });
                                }
                            }, 0);
                        } else {
                            // No suggestions for high-quality postings
                            window.currentSuggestions = [];
                            suggEl.innerHTML = '<p>No suggestions—looks great!</p>';
                        }
                    } else {
                        console.error('Analyze API error', analyzeResp.status);
                        window.currentSuggestions = [];
                        suggEl.innerHTML = '<p>Analysis failed.</p>';
                        scoreEl.textContent = '--%';
                        barEl.style.width = '0%';
                    }
                } catch (e) {
                    console.error('Analyze request failed', e);
                    suggEl.innerHTML = '<p>Analysis error.</p>';
                    scoreEl.textContent = '--%';
                    barEl.style.width = '0%';
                } finally {
                    if (spinner) spinner.classList.add('hidden');
                }
            }
            
        } catch (error) {
            console.error('Error generating job posting:', error);
            showError(`Error during generation: ${error.message}`);
            
            // Restore original form values
            jobTitleInput.value = originalValues.jobTitle;
            experienceInput.value = originalValues.experience;
            employmentTypeInput.value = originalValues.employmentType;
            keywordsInput.value = originalValues.keywords;
            platformInput.value = originalValues.platform;
            lengthInput.value = originalValues.length;
        } finally {
            loadingIndicator.classList.add('hidden');
            generateButton.disabled = false;
        }
    }

    // Copy job posting to clipboard
    if (copyButton) {
        copyButton.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(jobResult.innerText);
                showNotification('Job posting copied to clipboard!');
            } catch (error) {
                showError('Error copying: ' + error.message);
            }
        });
    }

    // Download job posting as text file
    if (downloadButton) {
        downloadButton.addEventListener('click', () => {
            try {
                const jobTitle = jobTitleInput.value.trim().replace(/[^a-z0-9]/gi, '_').toLowerCase();
                const filename = `job_posting_${jobTitle}_${new Date().toISOString().split('T')[0]}.md`;
                const content = jobResult.innerText;
                
                const element = document.createElement('a');
                element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content));
                element.setAttribute('download', filename);
                element.style.display = 'none';
                
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
                
                showNotification('Job posting downloaded!');
            } catch (error) {
                showError('Error downloading: ' + error.message);
            }
        });
    }
    
    // Download as Word (.docx)
    if (downloadDocxBtn) {
        downloadDocxBtn.addEventListener('click', async () => {
            try {
                // Build Word document using docx library
                // Support both window.docx and window.Docx globals
                const docxLib = window.docx || window.Docx;
                if (!docxLib) throw new Error('docx library is not loaded');
                const { Document, Packer, Paragraph } = docxLib;
                // Initialize Document with empty sections and basic metadata to avoid undefined errors
                const doc = new Document({ sections: [], creator: '' });
                const paragraphs = jobResult.innerText
                    .split('\n')
                    .map(line => new Paragraph(line));
                doc.addSection({ children: paragraphs });
                const blob = await Packer.toBlob(doc);
                const jobTitle = jobTitleInput.value.trim().replace(/[^a-z0-9]/gi, '_').toLowerCase();
                const filename = `job_posting_${jobTitle}_${new Date().toISOString().split('T')[0]}.docx`;
                saveAs(blob, filename);
                showNotification('Job posting downloaded as DOCX!');
            } catch (error) {
                showError('Error downloading DOCX: ' + error.message);
            }
        });
    }
    
    // Download as PDF with jsPDF (text-based PDF)
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            try {
                const { jsPDF } = window.jspdf;
                const doc = new jsPDF({ unit: 'pt', format: 'a4' });
                const margin = 40;
                const maxWidth = doc.internal.pageSize.getWidth() - margin * 2;
                const lineHeight = 14;
                let cursorY = margin;
                const textLines = doc.splitTextToSize(jobResult.innerText, maxWidth);
                textLines.forEach(line => {
                    if (cursorY + lineHeight > doc.internal.pageSize.getHeight() - margin) {
                        doc.addPage();
                        cursorY = margin;
                    }
                    doc.text(line, margin, cursorY);
                    cursorY += lineHeight;
                });
                const jobTitle = jobTitleInput.value.trim().replace(/[^a-z0-9]/gi, '_').toLowerCase();
                const filename = `job_posting_${jobTitle}_${new Date().toISOString().split('T')[0]}.pdf`;
                doc.save(filename);
                showNotification('Job posting downloaded as PDF!');
            } catch (error) {
                showError('Error downloading PDF: ' + error.message);
            }
        });
    }
    
    // Export to Google Docs
    if (exportGdocsBtn) {
        exportGdocsBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(jobResult.innerText);
                window.open('https://docs.new', '_blank');
                showNotification('Job posting copied! Paste into Google Docs.');
            } catch (error) {
                showError('Error exporting to Google Docs: ' + error.message);
            }
        });
    }
    
    // Help button for Google Docs export
    const exportGdocsHelpBtn = document.getElementById('export-gdocs-help');
    if (exportGdocsHelpBtn) {
        exportGdocsHelpBtn.addEventListener('click', () => {
            alert('Opens new Google Doc. Paste the content (Ctrl+V / Cmd+V).');
        });
    }

    // Show error notification
    function showError(message) {
        if (errorMessage && errorNotification) {
            errorMessage.textContent = message;
            errorNotification.classList.remove('hidden');
            
            setTimeout(() => {
                errorNotification.classList.add('hidden');
            }, 5000);
        }
    }

    // Show success notification
    function showNotification(message) {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 flex items-center space-x-2';
        notification.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Settings modal functionality
    const settingsModal = document.getElementById('settings-modal');
    const openSettingsBtn = document.getElementById('open-settings');
    const closeSettingsBtn = document.getElementById('close-settings');
    const cancelSettingsBtn = document.getElementById('cancel-settings');
    const settingsForm = document.getElementById('settings-form');

    if (openSettingsBtn && settingsModal) {
        openSettingsBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/settings');
                const data = await response.json();
                
                const prefCompanyName = document.getElementById('pref-company-name');
                if (prefCompanyName) {
                    prefCompanyName.value = data.company_name || '';
                }
                
                settingsModal.classList.remove('hidden');
            } catch (error) {
                console.error('Error loading settings:', error);
                settingsModal.classList.remove('hidden');
            }
        });
    }

    function hideSettingsModal() {
        if (settingsModal) {
            settingsModal.classList.add('hidden');
        }
    }

    if (closeSettingsBtn) closeSettingsBtn.addEventListener('click', hideSettingsModal);
    if (cancelSettingsBtn) cancelSettingsBtn.addEventListener('click', hideSettingsModal);
    
    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) hideSettingsModal();
        });
    }

    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const prefCompanyName = document.getElementById('pref-company-name');
            const prefs = {
                company_name: prefCompanyName ? prefCompanyName.value.trim() : ''
            };
            
            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(prefs)
                });
                
                if (response.ok) {
                    hideSettingsModal();
                    showNotification('Settings saved successfully!');
                } else {
                    showError('Failed to save settings');
                }
            } catch (error) {
                showError('Error saving settings: ' + error.message);
            }
        });
    }

    // Event listeners
    if (jobForm) {
        jobForm.addEventListener('submit', generateJobPosting);
    }
    
    // Initialize theme
    initTheme();
    
    // Accordion and progress logic
    function updateProgress(activeStep) {
        const steps = document.querySelectorAll('[data-step]');
        steps.forEach((step, idx) => {
            if (idx < activeStep) {
                step.classList.remove('text-gray-500');
                step.classList.add('text-blue-600', 'font-bold');
            } else {
                step.classList.add('text-gray-500');
                step.classList.remove('text-blue-600', 'font-bold');
            }
        });
    }
    updateProgress(1);
    const accordionHeaders = document.querySelectorAll('[data-accordion-header]');
    accordionHeaders.forEach((header, idx) => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            const icon = header.querySelector('[data-accordion-icon]');
            const isOpen = !content.classList.contains('hidden');
            content.classList.toggle('hidden');
            icon.textContent = isOpen ? '▶' : '▼';
            updateProgress(idx + 1);
        });
    });
    
    // Salary toggle
    const salaryToggle = document.getElementById('toggle-salary');
    if (salaryToggle) {
        salaryToggle.addEventListener('change', () => {
            const salaryRange = document.getElementById('salary-range');
            if (salaryRange) salaryRange.classList.toggle('hidden', !salaryToggle.checked);
        });
    }
    
    // Suggestions modal elements
    const suggestionsModal = document.getElementById('suggestions-modal');
    const suggestionsListDiv = document.getElementById('suggestions-list');
    const suggestionCommentInput = document.getElementById('suggestion-comment');
    const cancelSuggestionsBtn = document.getElementById('cancel-suggestions');
    const closeSuggestionsBtn = document.getElementById('close-suggestions');
    const applySuggestionsConfirmBtn = document.getElementById('apply-suggestions-confirm');
    if (suggestionsModal) {
        if (closeSuggestionsBtn) closeSuggestionsBtn.addEventListener('click', () => suggestionsModal.classList.add('hidden'));
        if (cancelSuggestionsBtn) cancelSuggestionsBtn.addEventListener('click', () => suggestionsModal.classList.add('hidden'));
        suggestionsModal.addEventListener('click', e => { if (e.target === suggestionsModal) suggestionsModal.classList.add('hidden'); });
    }
    
    // Apply suggestions confirmation
    if (applySuggestionsConfirmBtn) {
        applySuggestionsConfirmBtn.addEventListener('click', async () => {
        // Close suggestions modal and show loading indicator for apply-suggestions
        if (suggestionsModal) suggestionsModal.classList.add('hidden');
        if (loadingIndicator) loadingIndicator.classList.remove('hidden');
        if (generatedContent) generatedContent.classList.add('hidden');
            try {
                applySuggestionsConfirmBtn.disabled = true;
                // Apply suggestions to current posting
                const original = jobResult.innerText;
                const suggestions = window.currentSuggestions || [];
                const comment = suggestionCommentInput.value.trim();
                const payload = { original_posting: original, suggestions, suggestion_comment: comment };
                const resp = await fetch('/api/generate/apply-suggestions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                
                // Stream the improved posting
                const reader = resp.body.getReader();
                const decoder = new TextDecoder();
                let partial = '';
                
                // Reset display and show generated content area
                jobResult.innerHTML = '';
                generatedContent.classList.remove('hidden');
                
                // Read stream progressively
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    partial += decoder.decode(value, { stream: true });
                    jobResult.innerHTML = formatContent(partial);
                }
                
                reader.releaseLock();
                
                // Hide loading indicator after streaming completes
                if (loadingIndicator) loadingIndicator.classList.add('hidden');
                
                // Add syntax highlighting
                if (typeof hljs !== 'undefined') {
                    jobResult.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
                }
                
                // Update quality display
                const scoreEl = document.getElementById('quality-score');
                const barEl = document.getElementById('quality-bar');
                const suggEl = document.getElementById('suggestions');
                if (scoreEl && barEl && suggEl) {
                    scoreEl.textContent = '100%';
                    barEl.style.width = '100%';
                    suggEl.innerHTML = '<p>No suggestions—looks great!</p>';
                }
                showNotification('Suggestions applied!');
            } catch (error) {
                showError('Error applying suggestions: ' + error.message);
            } finally {
                applySuggestionsConfirmBtn.disabled = false;
                if (loadingIndicator) loadingIndicator.classList.add('hidden');
            }
        });
    }

    // Salary toggle functionality
    if (salaryToggleInput) {
        salaryToggleInput.addEventListener('change', () => {
            const salarySection = document.getElementById('salary-range-section');
            if (salarySection) {
                if (salaryToggleInput.checked) {
                    salarySection.classList.remove('hidden');
                } else {
                    salarySection.classList.add('hidden');
                }
            }
        });
    }

    // Note: Accordion functionality already handled above at line 828

    // Smart content analysis for job overview
    if (jobOverviewInput) {
        jobOverviewInput.addEventListener('input', () => {
            const content = jobOverviewInput.value.trim();
            const smartHintTrigger = document.getElementById('smart-hint-trigger');
            const scenarioGuide = document.getElementById('scenario-a-guide');
            
            if (content.length > 200) {
                // Show smart hint for complete content
                if (smartHintTrigger) smartHintTrigger.classList.remove('hidden');
                if (scenarioGuide) scenarioGuide.classList.remove('hidden');
            } else {
                // Hide hints for short content
                if (smartHintTrigger) smartHintTrigger.classList.add('hidden');
                if (scenarioGuide) scenarioGuide.classList.add('hidden');
            }
        });
    }
    
    // Initialize
    initTheme();
});
# Code Architecture Documentation

## 🏗️ Overall Architecture

The Berlin Business Assessment Tool follows a **single-page application (SPA)** architecture with vanilla JavaScript for maximum performance and minimal dependencies.

## 📁 File Structure

```
index.html                  # Monolithic SPA containing all code
├── HTML Structure          # Semantic markup
├── CSS Styling            # Component-based styles
└── JavaScript Logic       # Assessment functionality
```

## 🎨 CSS Architecture

### 1. CSS Custom Properties (Variables)
```css
:root {
    --primary: #6366f1;      /* Brand colors */
    --secondary: #8b5cf6;
    --accent: #06b6d4;
    --background: #0f0f23;   /* Layout colors */
    --surface: rgba(255, 255, 255, 0.05);
    --text-primary: #ffffff; /* Typography colors */
}
```

### 2. Component-Based Styling
Each UI component has dedicated CSS classes:

```css
/* Hero Section */
.hero { }
.hero-content { }
.logo-container { }

/* Question Components */
.question-section { }
.question-header { }
.option { }
.option-content { }

/* Navigation */
.navigation { }
.nav-btn { }
```

### 3. Responsive Design Strategy
```css
/* Mobile First Approach */
.benefits-grid {
    grid-template-columns: repeat(2, 1fr); /* Mobile default */
}

@media (min-width: 1024px) {
    .benefits-grid {
        grid-template-columns: repeat(4, 1fr); /* Desktop override */
    }
}
```

## ⚙️ JavaScript Architecture

### 1. Class-Based Organization
```javascript
class AssessmentApp {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.totalQuestions = 5;
    }
    
    // Core methods
    init() { }
    nextQuestion() { }
    prevQuestion() { }
    submitAssessment() { }
}
```

### 2. Event-Driven Architecture
```javascript
// Initialization
document.addEventListener('DOMContentLoaded', () => {
    const app = new AssessmentApp();
    app.init();
});

// User interactions
document.getElementById('nextBtn').addEventListener('click', () => this.nextQuestion());
document.addEventListener('keydown', (e) => this.handleKeyboard(e));
```

### 3. State Management
```javascript
// Application state stored in class properties
this.currentQuestion = 0;        // Current question index
this.answers = {};              // User responses
this.totalQuestions = 5;        // Total questions count
```

## 🧩 Component Breakdown

### 1. Progress Bar Component
```css
.progress-container { }         /* Fixed container */
.progress-bar { }              /* Animated progress */
```
```javascript
updateProgress() {
    const percentage = (this.currentQuestion / this.totalQuestions) * 100;
    document.getElementById('progressBar').style.width = `${percentage}%`;
}
```

### 2. Question Component
```html
<section class="question-section" data-question="1">
    <div class="question-header">
        <div class="question-number">1</div>
        <h3 class="question-title">Question text</h3>
    </div>
    <div class="options-container">
        <!-- Radio button options -->
    </div>
</section>
```

### 3. Option Component
```html
<label class="option">
    <input type="radio" name="question_name" value="option_value" required>
    <div class="option-content">
        <div class="option-icon">
            <i class="fas fa-icon"></i>
        </div>
        <div class="option-text">Option description</div>
    </div>
</label>
```

### 4. Navigation Component
```html
<nav class="navigation">
    <button type="button" class="nav-btn nav-btn-secondary" id="prevBtn">
        <i class="fas fa-arrow-left"></i>Zurück
    </button>
    <div class="question-counter">
        <span id="questionCounter">Frage 1 von 5</span>
    </div>
    <button type="button" class="nav-btn nav-btn-primary" id="nextBtn">
        Weiter<i class="fas fa-arrow-right"></i>
    </button>
</nav>
```

## 🔄 Data Flow

### 1. User Interaction Flow
```
User clicks option → Radio button selected → Answer stored → Navigation enabled → Next question
```

### 2. Form Submission Flow
```
All questions answered → Contact form shown → User fills form → Data submitted → Results displayed
```

### 3. State Updates
```javascript
// Answer selection
radio.addEventListener('change', (e) => {
    this.answers[radio.name] = radio.value;
    this.updateNextButton();
});

// Question navigation
nextQuestion() {
    this.currentQuestion++;
    this.showQuestion(this.currentQuestion);
    this.updateProgress();
    this.updateNavigation();
}
```

## 🎯 Design Patterns Used

### 1. **Single Responsibility Principle**
Each method has one clear purpose:
- `showQuestion()` - Display specific question
- `updateProgress()` - Update progress bar
- `validateForm()` - Check form completion

### 2. **Observer Pattern**
Event listeners observe user interactions:
```javascript
// Radio button changes
radio.addEventListener('change', (e) => this.handleAnswerChange(e));

// Keyboard events
document.addEventListener('keydown', (e) => this.handleKeyboard(e));
```

### 3. **Module Pattern**
Self-contained functionality:
```javascript
class AssessmentApp {
    // Private methods (convention with _)
    _showLoadingOverlay() { }
    _hideLoadingOverlay() { }
    
    // Public interface
    init() { }
    nextQuestion() { }
}
```

## 🔧 Utility Functions

### 1. Animation Helpers
```javascript
// Smooth scrolling
scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Element visibility
showElement(element) {
    element.style.display = 'block';
    element.classList.add('show');
}
```

### 2. Validation Helpers
```javascript
// Form validation
validateContactForm() {
    const requiredFields = ['firstName', 'lastName', 'email', 'company'];
    return requiredFields.every(field => 
        document.getElementById(field).value.trim() !== ''
    );
}
```

## 🎨 Animation System

### 1. CSS Transitions
```css
.question-section {
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0;
    transform: translateX(100px);
}

.question-section.visible {
    opacity: 1;
    transform: translateX(0);
}
```

### 2. Progressive Enhancement
```javascript
// Animation with fallbacks
showQuestion(index) {
    const question = document.querySelector(`[data-question="${index + 1}"]`);
    if (question) {
        question.classList.add('visible');
        if (index === this.currentQuestion) {
            question.classList.add('current');
        }
    }
}
```

## 📱 Responsive Architecture

### 1. Mobile-First CSS
```css
/* Base styles for mobile */
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

/* Progressive enhancement for larger screens */
@media (min-width: 1024px) {
    .benefits-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }
}
```

### 2. Adaptive JavaScript
```javascript
// Touch vs. mouse interactions
const isTouchDevice = 'ontouchstart' in window;
if (isTouchDevice) {
    // Touch-specific enhancements
}
```

## 🔒 Security Considerations

### 1. Input Sanitization
```javascript
// Basic XSS prevention
sanitizeInput(input) {
    return input.replace(/[<>]/g, '');
}
```

### 2. Form Validation
```javascript
// Client-side validation (server-side still required)
validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
```

## 🚀 Performance Optimizations

### 1. Minimal Dependencies
- No external JavaScript frameworks
- Selective Font Awesome icons
- Optimized Google Fonts loading

### 2. Efficient DOM Manipulation
```javascript
// Cache DOM queries
constructor() {
    this.progressBar = document.getElementById('progressBar');
    this.questionCounter = document.getElementById('questionCounter');
}
```

### 3. CSS Optimizations
```css
/* Hardware acceleration for animations */
.option {
    transform: translateZ(0);
    will-change: transform;
}

/* Efficient backdrop filters */
.hero {
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
}
```

## 🧪 Testing Considerations

### 1. Manual Testing Checklist
- [ ] All questions display correctly
- [ ] Navigation works in both directions
- [ ] Form validation prevents incomplete submissions
- [ ] Responsive design works on all devices
- [ ] Keyboard navigation functions properly

### 2. Automated Testing Potential
```javascript
// Future test structure
describe('AssessmentApp', () => {
    test('should initialize with correct default state', () => {
        const app = new AssessmentApp();
        expect(app.currentQuestion).toBe(0);
        expect(app.answers).toEqual({});
    });
});
```

## 🔄 Future Architecture Improvements

### 1. Component Separation
Split monolithic file into:
- `components/Question.js`
- `components/Navigation.js`
- `utils/validation.js`
- `styles/components.css`

### 2. State Management
Implement proper state management:
```javascript
class StateManager {
    constructor() {
        this.state = {
            currentQuestion: 0,
            answers: {},
            isLoading: false
        };
        this.observers = [];
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifyObservers();
    }
}
```

### 3. API Integration
Structure for future backend integration:
```javascript
class APIService {
    async submitAssessment(data) {
        const response = await fetch('/api/assessment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
}
```

---

This architecture prioritizes **maintainability**, **performance**, and **user experience** while keeping the codebase simple and understandable.
// Aptitude Test Application
class AptitudeTest {
    constructor() {
        this.currentQuestions = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = [];
        this.startTime = null;
        this.endTime = null;
        this.timerInterval = null;
        this.usedQuestionIds = new Set();
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        // Screens
        this.welcomeScreen = document.getElementById('welcome-screen');
        this.testScreen = document.getElementById('test-screen');
        this.resultsScreen = document.getElementById('results-screen');

        // Welcome screen elements
        this.startTestBtn = document.getElementById('start-test');

        // Test screen elements
        this.questionCounter = document.getElementById('question-counter');
        this.progressFill = document.getElementById('progress-fill');
        this.timeDisplay = document.getElementById('time-display');
        this.questionText = document.getElementById('question-text');
        this.optionsContainer = document.getElementById('options-container');
        this.prevQuestionBtn = document.getElementById('prev-question');
        this.clearSelectionBtn = document.getElementById('clear-selection');
        this.nextQuestionBtn = document.getElementById('next-question');
        this.submitTestBtn = document.getElementById('submit-test');

        // Results screen elements
        this.scorePercentage = document.getElementById('score-percentage');
        this.totalQuestions = document.getElementById('total-questions');
        this.correctAnswers = document.getElementById('correct-answers');
        this.wrongAnswers = document.getElementById('wrong-answers');
        this.timeTaken = document.getElementById('time-taken');
        this.categoryPerformance = document.getElementById('category-performance');
        this.answerReviewContainer = document.getElementById('answer-review-container');
        this.retakeTestBtn = document.getElementById('retake-test');
        this.newTestBtn = document.getElementById('new-test');
    }

    attachEventListeners() {
        this.startTestBtn.addEventListener('click', () => this.startTest());
        this.prevQuestionBtn.addEventListener('click', () => this.previousQuestion());
        this.clearSelectionBtn.addEventListener('click', () => this.clearCurrentSelection());
        this.nextQuestionBtn.addEventListener('click', () => this.nextQuestion());
        this.submitTestBtn.addEventListener('click', () => this.submitTest());
        this.retakeTestBtn.addEventListener('click', () => this.retakeTest());
        this.newTestBtn.addEventListener('click', () => this.newTest());
    }

    startTest() {
        // Generate 10 random questions that haven't been used before
        this.currentQuestions = getRandomQuestions(10, Array.from(this.usedQuestionIds));
        this.currentQuestionIndex = 0;
        this.userAnswers = new Array(10).fill(null);
        this.startTime = new Date();
        
        // Mark these questions as used
        this.currentQuestions.forEach(q => this.usedQuestionIds.add(q.id));

        // Switch to test screen
        this.showScreen('test');
        
        // Display first question
        this.displayQuestion();
        
        // Start timer
        this.startTimer();
    }

    displayQuestion() {
        const question = this.currentQuestions[this.currentQuestionIndex];
        
        // Update question counter and progress
        this.questionCounter.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.currentQuestions.length}`;
        this.progressFill.style.width = `${((this.currentQuestionIndex + 1) / this.currentQuestions.length) * 100}%`;
        
        // Display question text
        this.questionText.textContent = question.question;
        
        // Clear and populate options
        this.optionsContainer.innerHTML = '';
        question.options.forEach((option, index) => {
            const optionElement = this.createOptionElement(option, index);
            this.optionsContainer.appendChild(optionElement);
        });
        
        // Restore user's previous answer if exists
        if (this.userAnswers[this.currentQuestionIndex] !== null) {
            const selectedOption = this.optionsContainer.querySelector(`input[value="${this.userAnswers[this.currentQuestionIndex]}"]`);
            if (selectedOption) {
                selectedOption.checked = true;
                selectedOption.parentElement.classList.add('selected');
            }
        }
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }

    createOptionText(option, index) {
        const letters = ['A', 'B', 'C', 'D'];
        return `
            <div class="option">
                <label class="option-label">
                    <input type="radio" name="answer" value="${index}">
                    <span class="option-letter">${letters[index]}</span>
                    <span class="option-text">${option}</span>
                </label>
            </div>
        `;
    }

    createOptionElement(option, index) {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.innerHTML = `
            <label class="option-label">
                <input type="radio" name="answer" value="${index}">
                <span class="option-letter">${String.fromCharCode(65 + index)}</span>
                <span class="option-text">${option}</span>
            </label>
        `;
        
        // Add click event to select option
        optionDiv.addEventListener('click', () => {
            const radio = optionDiv.querySelector('input[type="radio"]');
            radio.checked = true;
            this.updateOptionSelection();
            this.userAnswers[this.currentQuestionIndex] = index;
        });
        
        return optionDiv;
    }

    updateOptionSelection() {
        const options = this.optionsContainer.querySelectorAll('.option');
        options.forEach(option => {
            const radio = option.querySelector('input[type="radio"]');
            if (radio.checked) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }

    clearCurrentSelection() {
        const selectedRadio = this.optionsContainer.querySelector('input[type="radio"]:checked');
        if (selectedRadio) {
            selectedRadio.checked = false;
            this.userAnswers[this.currentQuestionIndex] = null;
        }
        this.updateOptionSelection();
    }

    updateNavigationButtons() {
        // Previous button
        this.prevQuestionBtn.disabled = this.currentQuestionIndex === 0;
        
        // Next/Submit button
        if (this.currentQuestionIndex === this.currentQuestions.length - 1) {
            this.nextQuestionBtn.style.display = 'none';
            this.submitTestBtn.style.display = 'inline-block';
        } else {
            this.nextQuestionBtn.style.display = 'inline-block';
            this.submitTestBtn.style.display = 'none';
        }
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayQuestion();
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.currentQuestions.length - 1) {
            this.currentQuestionIndex++;
            this.displayQuestion();
        }
    }

    submitTest() {
        // Check if all questions are answered
        const unansweredQuestions = this.userAnswers.filter(answer => answer === null).length;
        if (unansweredQuestions > 0) {
            if (!confirm(`You have ${unansweredQuestions} unanswered question(s). Do you want to submit anyway?`)) {
                return;
            }
        }
        
        this.endTime = new Date();
        this.stopTimer();
        this.calculateResults();
        this.showResults();
    }

    calculateResults() {
        let correctCount = 0;
        const categoryResults = {};
        
        this.currentQuestions.forEach((question, index) => {
            const userAnswer = this.userAnswers[index];
            const isCorrect = userAnswer === question.correctAnswer;
            
            if (isCorrect) {
                correctCount++;
            }
            
            // Track category performance
            if (!categoryResults[question.category]) {
                categoryResults[question.category] = { correct: 0, total: 0 };
            }
            categoryResults[question.category].total++;
            if (isCorrect) {
                categoryResults[question.category].correct++;
            }
        });
        
        this.results = {
            totalQuestions: this.currentQuestions.length,
            correctAnswers: correctCount,
            wrongAnswers: this.currentQuestions.length - correctCount,
            percentage: Math.round((correctCount / this.currentQuestions.length) * 100),
            categoryResults: categoryResults,
            timeTaken: this.endTime - this.startTime,
            questions: this.currentQuestions.map((question, index) => ({
                question: question.question,
                options: question.options,
                correctAnswer: question.correctAnswer,
                userAnswer: this.userAnswers[index],
                category: question.category
            }))
        };
    }

    showResults() {
        this.showScreen('results');
        
        // Display score summary
        this.scorePercentage.textContent = `${this.results.percentage}%`;
        this.totalQuestions.textContent = this.results.totalQuestions;
        this.correctAnswers.textContent = this.results.correctAnswers;
        this.wrongAnswers.textContent = this.results.wrongAnswers;
        this.timeTaken.textContent = this.formatTime(this.results.timeTaken);
        
        // Display category performance
        this.displayCategoryPerformance();
        
        // Display answer review
        this.displayAnswerReview();
    }

    displayCategoryPerformance() {
        this.categoryPerformance.innerHTML = '';
        
        Object.entries(this.results.categoryResults).forEach(([category, data]) => {
            const percentage = Math.round((data.correct / data.total) * 100);
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'category-item';
            categoryDiv.innerHTML = `
                <div class="category-name">${category}</div>
                <div class="category-score">${data.correct}/${data.total} (${percentage}%)</div>
            `;
            this.categoryPerformance.appendChild(categoryDiv);
        });
    }

    displayAnswerReview() {
        this.answerReviewContainer.innerHTML = '';
        
        this.results.questions.forEach((item, index) => {
            const reviewDiv = document.createElement('div');
            reviewDiv.className = `review-item ${item.userAnswer === item.correctAnswer ? 'correct' : 'wrong'}`;
            
            const userAnswerText = item.userAnswer !== null ? item.options[item.userAnswer] : 'Not answered';
            const correctAnswerText = item.options[item.correctAnswer];
            
            reviewDiv.innerHTML = `
                <div class="review-question">Q${index + 1}: ${item.question}</div>
                <div class="review-answer ${item.userAnswer === item.correctAnswer ? 'correct' : 'wrong'}">
                    Your answer: ${userAnswerText}
                </div>
                <div class="review-answer correct">Correct answer: ${correctAnswerText}</div>
                <div class="review-category">Category: ${item.category}</div>
            `;
            
            this.answerReviewContainer.appendChild(reviewDiv);
        });
    }

    retakeTest() {
        // Retake the same questions
        this.currentQuestionIndex = 0;
        this.userAnswers = new Array(this.currentQuestions.length).fill(null);
        this.startTime = new Date();
        this.endTime = null;
        
        this.showScreen('test');
        this.displayQuestion();
        this.startTimer();
    }

    newTest() {
        // Generate completely new questions
        this.startTest();
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = new Date() - this.startTime;
            this.timeDisplay.textContent = this.formatTime(elapsed);
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    showScreen(screenName) {
        // Hide all screens
        this.welcomeScreen.classList.remove('active');
        this.testScreen.classList.remove('active');
        this.resultsScreen.classList.remove('active');
        
        // Show selected screen
        switch(screenName) {
            case 'welcome':
                this.welcomeScreen.classList.add('active');
                break;
            case 'test':
                this.testScreen.classList.add('active');
                break;
            case 'results':
                this.resultsScreen.classList.add('active');
                break;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const testApp = new AptitudeTest();
    
    // Make the app globally accessible for debugging
    window.aptitudeTest = testApp;
});

// Utility function to format time in minutes and seconds
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Utility function to shuffle array
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

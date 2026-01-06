/**
 * Timer functionality for exam time management
 */

class ExamTimer {
    constructor(elementId, initialSeconds, onExpire) {
        this.element = document.getElementById(elementId);
        this.seconds = initialSeconds;
        this.onExpire = onExpire;
        this.interval = null;
    }

    start() {
        this.update();
        this.interval = setInterval(() => this.tick(), 1000);
    }

    tick() {
        this.seconds--;
        this.update();

        if (this.seconds <= 0) {
            this.stop();
            if (this.onExpire) {
                this.onExpire();
            }
        }

        // Warning when less than 5 minutes
        if (this.seconds <= 300) {
            this.element.classList.add('warning');
        }
    }

    update() {
        const minutes = Math.floor(this.seconds / 60);
        const secs = this.seconds % 60;
        this.element.textContent =
            `⏱️ ${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }
}

/**
 * Auto-save answer when selected
 */
function saveAnswer(attemptId, questionId, answer) {
    const formData = new FormData();
    formData.append('attempt_id', attemptId);
    formData.append('question_id', questionId);
    formData.append('selected_answer', answer);

    fetch('/student/answer-form', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSaveIndicator(questionId);
            }
        })
        .catch(error => {
            console.error('Error saving answer:', error);
        });
}

/**
 * Show save indicator
 */
function showSaveIndicator(questionId) {
    const card = document.querySelector(`#question-${questionId}`);
    if (card) {
        const indicator = document.createElement('span');
        indicator.textContent = '✓ Kaydedildi';
        indicator.className = 'save-indicator';
        indicator.style.cssText = `
            position: absolute;
            top: 1rem;
            right: 1rem;
            color: #10b981;
            font-size: 0.875rem;
            animation: fadeOut 2s forwards;
        `;
        card.style.position = 'relative';
        card.appendChild(indicator);

        setTimeout(() => indicator.remove(), 2000);
    }
}

/**
 * Auto-submit exam when time expires
 */
function autoSubmitExam(formId) {
    const form = document.getElementById(formId);
    if (form) {
        alert('⏰ Süre doldu! Sınavınız otomatik olarak gönderiliyor.');
        form.submit();
    }
}

/**
 * Confirm before leaving exam page
 */
function setupExitConfirmation() {
    window.addEventListener('beforeunload', function (e) {
        e.preventDefault();
        e.returnValue = '';
        return 'Sınavdan çıkmak istediğinize emin misiniz? Cevaplarınız kaydedilecektir.';
    });
}

/**
 * Add fadeOut animation
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        0% { opacity: 1; }
        70% { opacity: 1; }
        100% { opacity: 0; }
    }
`;
document.head.appendChild(style);

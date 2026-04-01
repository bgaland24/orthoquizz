/* ================================================================
   QUIZ-QUESTION.JS — Timer, clic sur les mots, feedback
   Les données sont lues depuis les data-attributes du formulaire.
   ================================================================ */

const form            = document.getElementById('answerForm');
const correctPosition = parseInt(form.dataset.correctPosition);
const tempsLimite     = parseInt(form.dataset.tempsLimite);
const motCorrige      = form.dataset.motCorrige;

let tempsRestant = tempsLimite;
let answered     = false;
let timerInterval;

function startTimer() {
    updateTimerBar();
    timerInterval = setInterval(() => {
        tempsRestant--;
        updateTimerBar();
        if (tempsRestant <= 0) {
            clearInterval(timerInterval);
            handleTimeout();
        }
    }, 1000);
}

function updateTimerBar() {
    const pct = Math.max(0, (tempsRestant / tempsLimite) * 100);
    const bar = document.getElementById('timerBar');
    bar.style.width = pct + '%';
    if (pct > 60)
        bar.style.background = 'linear-gradient(90deg, #2ecc71, #27ae60)';
    else if (pct > 30)
        bar.style.background = 'linear-gradient(90deg, #f39c12, #e67e22)';
    else
        bar.style.background = 'linear-gradient(90deg, #e74c3c, #c0392b)';
    document.getElementById('timerText').textContent = tempsRestant + 's';
}

function handleWordClick(position, el) {
    if (answered) return;
    answered = true;
    clearInterval(timerInterval);
    position = parseInt(position);

    document.getElementById('position_cliquee').value = position;
    document.getElementById('temps_restant').value    = tempsRestant;

    document.querySelectorAll('.word-btn').forEach(w => w.disabled = true);

    if (position === correctPosition) {
        el.classList.add('word-correct');
        showFeedback('bravo');
    } else {
        el.classList.add('word-incorrect');
        document.querySelectorAll('.word-btn')[correctPosition].classList.add('word-hint');
        showFeedback('erreur');
    }
    document.getElementById('nextBtn').classList.remove('hidden');
}

function handleTimeout() {
    if (answered) return;
    answered = true;
    document.getElementById('position_cliquee').value = -1;
    document.getElementById('temps_restant').value    = 0;
    document.querySelectorAll('.word-btn').forEach(w => w.disabled = true);
    document.querySelectorAll('.word-btn')[correctPosition].classList.add('word-hint');
    showFeedback('timeout');
    document.getElementById('nextBtn').classList.remove('hidden');
}

function showFeedback(type) {
    const el = document.getElementById('feedback');
    el.classList.remove('hidden');
    const messages = {
        bravo:   { cls: 'feedback feedback-success', prefix: '✅ Bravo\u00a0! La bonne orthographe est\u00a0: ' },
        erreur:  { cls: 'feedback feedback-error',   prefix: '❌ Tu n\'es pas passé loin\u00a0! La bonne orthographe est\u00a0: ' },
        timeout: { cls: 'feedback feedback-timeout', prefix: '⏰ Temps écoulé\u00a0! La bonne orthographe était\u00a0: ' },
    };
    const { cls, prefix } = messages[type] || messages.timeout;
    el.className = cls;
    el.textContent = '';
    const span   = document.createElement('span');
    span.textContent = prefix;
    const strong = document.createElement('strong');
    strong.textContent = motCorrige;
    el.appendChild(span);
    el.appendChild(strong);
}

document.querySelectorAll('.word-btn').forEach(btn => {
    btn.addEventListener('click', () => handleWordClick(btn.dataset.index, btn));
});

startTimer();

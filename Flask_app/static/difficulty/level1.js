let currentQuestionIndex = 0;
let answeredQuestions = new Set();  // Keep track of answered questions
let totalQuestions = 0;  // 총 질문 수 저장
let questionCodes = [];  // question_code 리스트 저장

function startTimer() {
    let timerElement = document.getElementById('timer');
    let seconds = 0;
    setInterval(() => {
        seconds++;
        timerElement.textContent = `진행시간: ${seconds}초`;
    }, 1000);
}

function fetchQuestionCodes(articleCode) {
    const apiUrl = `http://${window.location.hostname}:8000/api/questions/questions_by_article_code?article_code=${articleCode}`;
    
    return fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(data); // 디버깅을 위해 데이터 출력
            questionCodes = data.question_codes;
        })
        .catch(error => {
            console.error('Error fetching question codes:', error);
        });
}

function loadQuestion(index) {
    const difficulty = localStorage.getItem('difficulty') || 'short'; // 기본값을 'short'로 설정
    const articleCode = localStorage.getItem('article_code') || 'ART-001-short'; // 기본값을 'ART-001-short'으로 설정
    const apiUrl = `http://${window.location.hostname}:8000/api/questions/Difficulty/level1/data?difficulty=${difficulty}&article_code=${articleCode}&index=${index}`; // 동적으로 호스트 이름을 사용하여 URL 생성
    console.log(`API URL: ${apiUrl}`);  // 디버깅 로그 추가
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(data); // 디버깅을 위해 데이터 출력
            if (data) {
                document.getElementById('article-title').textContent = data.articles[0].title;
                document.getElementById('article-date').textContent = data.articles[0].date;
                document.getElementById('article-author').textContent = data.articles[0].author;
                document.getElementById('article-paragraph1').textContent = data.articles[0].paragraph1;
                document.getElementById('article-paragraph2').textContent = data.articles[0].paragraph2;
                document.getElementById('article-paragraph3').textContent = data.articles[0].paragraph3;
                document.getElementById('article-paragraph4').textContent = data.articles[0].paragraph4;

                document.getElementById('question').textContent = data.questions[index].question;
                const answerElement = document.getElementById('answer');
                answerElement.innerHTML = ''; // Clear previous answers

                const options = data.questions[index].options;

                // Check if options are "A", "B", "C", "D"
                const isMCQ = options.every(option => ["A", "B", "C", "D"].includes(option));

                if (isMCQ) {
                    // If options are A, B, C, D, create a text box instead of radio buttons
                    const input = document.createElement('textarea');
                    input.name = 'answer';
                    input.setAttribute("cols", 10);
                    input.setAttribute("rows", 20);
                    input.oninput = () => saveAnswer(index, input.value);  // Save answer on input
                    answerElement.appendChild(input);
                } else {
                    // Create radio buttons for options
                    options.forEach((option, i) => {
                        const label = document.createElement('label');
                        const input = document.createElement('input');
                        input.type = 'radio';
                        input.name = 'answer';
                        input.value = option;
                        input.onclick = () => saveAnswer(index, option);  // Save answer on click
                        label.appendChild(input);
                        label.appendChild(document.createTextNode(option));
                        answerElement.appendChild(label);
                        answerElement.appendChild(document.createElement('br'));
                    });
                }
                
                loadSavedAnswer(index);  // Load saved answer for the current question
                currentQuestionIndex = index;
                totalQuestions = data.total;  // 총 질문 수 저장
                updateProgressIndicator();  // Initialize progress boxes
                updateButtons(currentQuestionIndex, totalQuestions);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function updateButtons(index, total) {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');

    prevButton.style.display = index > 0 ? 'block' : 'none';
    nextButton.style.display = index < total - 1 ? 'block' : 'none';
}

function nextQuestion() {
    if (currentQuestionIndex < totalQuestions - 1) {
        loadQuestion(currentQuestionIndex + 1);
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        loadQuestion(currentQuestionIndex - 1);
    }
}

function goToDashboard() {
    const articleCode = localStorage.getItem('article_code') || 'ART-001-short';  // article_code 가져오기
    window.location.href = `/dashboard?article_code=${articleCode}`;
}

function saveAnswer(index, answer) {
    const questionCode = questionCodes[index];
    localStorage.setItem(`question_${questionCode}`, answer);
    answeredQuestions.add(index);  // Add the question index to the set
    updateProgressIndicator();  // Update progress indicator
}

function loadSavedAnswer(index) {
    const questionCode = questionCodes[index];
    const savedAnswer = localStorage.getItem(`question_${questionCode}`);
    if (savedAnswer) {
        const inputs = document.querySelectorAll(`input[name="answer"]`);
        inputs.forEach(input => {
            if (input.value === savedAnswer) {
                input.checked = true;
            }
        });
        answeredQuestions.add(index);  // Add the question index to the set
    }
    updateProgressIndicator();
}

function updateProgressIndicator() {
    const progressIndicator = document.getElementById('progress-indicator');
    progressIndicator.innerHTML = '';  // Clear previous progress boxes

    for (let i = 0; i < totalQuestions; i++) {
        const box = document.createElement('div');
        box.classList.add('progress-box');
        if (answeredQuestions.has(i)) {
            box.classList.add('active');
        }
        progressIndicator.appendChild(box);
    }
}

window.onload = async () => {
    const articleCode = localStorage.getItem('article_code') || 'ART-001-short'; // 기본값을 'ART-001-short'으로 설정
    await fetchQuestionCodes(articleCode); // question_codes를 가져온 후에 타이머와 질문을 로드합니다.
    startTimer();
    loadQuestion(currentQuestionIndex);
}

function submitAllAnswers() {
    const answers = [];
    const userId = 1;  // 예시 사용자 ID, 실제 사용자 ID로 교체하세요.
    const articleCode = localStorage.getItem('article_code');  // article_code 가져오기

    if (!articleCode) {
        alert('article_code가 설정되지 않았습니다.');
        return;
    }

    for (let i = 0; i < totalQuestions; i++) {
        const questionCode = questionCodes[i];
        const savedAnswer = localStorage.getItem(`question_${questionCode}`);
        console.log("savedAnswer:", savedAnswer);
        if (savedAnswer) {
            answers.push({
                user_id: userId,
                article_code: articleCode,
                question_code: questionCode,
                submitted_answer: savedAnswer
            });
        } else {
            alert(`질문 ${i + 1}에 대한 답변을 선택해주세요.`);
            return;
        }
    }

    console.log("Submitting answers:", answers);  // 디버깅 로그 추가

    fetch('/submit_answers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        window.location.href = `/dashboard?article_code=${articleCode}`;
    })
    .catch(error => {
        console.error('에러:', error);
        window.location.href = `/dashboard?article_code=${articleCode}`;
    });
}

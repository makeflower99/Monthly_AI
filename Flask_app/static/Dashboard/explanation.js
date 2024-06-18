document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.problem-explanation');

    // 메타 태그에서 article_code를 가져옴
    const metaArticleCode = document.querySelector('meta[name="article_code"]');
    if (!metaArticleCode) {
        console.error("Meta tag with name 'article_code' is missing.");
        return;
    }

    const articleCode = metaArticleCode.getAttribute('content');
    console.log(`Loaded article_code: ${articleCode}`);

    // 로컬 스토리지에서 데이터를 가져와서 localQuestionsData 객체에 저장
    const localQuestionsData = {};

    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('question_')) {
            const value = localStorage.getItem(key).trim();
            localQuestionsData[key] = value;
            console.log(`Loaded ${key}: ${value}`);
        }
    }

    // 키 값을 기준으로 정렬
    const sortedKeys = Object.keys(localQuestionsData).sort((a, b) => {
        const aNum = parseInt(a.split('_')[1], 10);
        const bNum = parseInt(b.split('_')[1], 10);
        return aNum - bNum;
    });

    // 각 섹션에 대해 데이터를 매핑하고 정답 체크
    sections.forEach((section, index) => {
        const questionNumber = sortedKeys[index];
        const localQuestion = localQuestionsData[questionNumber] || null;

        const questionTextElement = section.querySelector('.question p');
        const answerTextElement = section.querySelector('.explanation p');

        if (!questionTextElement || !answerTextElement) {
            console.error(`Question or answer element missing in section ${index + 1}`);
            return;
        }

        const questionText = questionTextElement.textContent.trim();
        const answerText = answerTextElement.textContent.trim();

        if (index === sections.length - 1) {
            // 마지막 섹션에 대해서는 요약으로 제목 변경 및 정답 체크 제외
            section.querySelector('h2').textContent = '요약';
            section.querySelector('h3').textContent = 'AI가 작성한 요약';

            // 보기 영역을 숨기고 입력한 답을 표시
            const optionsList = section.querySelector('.question ul');
            if (optionsList) {
                optionsList.style.display = 'none';
            }

            // 로컬 스토리지에서 마지막 질문의 답을 요약 부분에 추가
            const lastQuestionKey = sortedKeys[sortedKeys.length - 1];
            const lastAnswer = localQuestionsData[lastQuestionKey];

            const summaryElement = document.createElement('p');
            summaryElement.textContent = lastAnswer;
            section.querySelector('.question').appendChild(summaryElement);

            return;
        }

        console.log(`Question ${index + 1}: ${questionText}`);
        console.log(`Answer ${index + 1}: ${answerText}`);
        console.log(`Local Question ${questionNumber}: ${localQuestion}`);

        const options = section.querySelectorAll('.question ul li');
        let isCorrect = false;

        options.forEach(option => {
            const optionText = option.textContent.trim();
            console.log(`Option: ${optionText}`);

            if (localQuestion && optionText === localQuestion) {
                console.log(`Selected answer: ${optionText}`);
                option.style.color = 'red';
                option.classList.add('selected');
            }

            if (answerText && optionText === answerText) {
                console.log(`Correct answer: ${optionText}`);
                option.style.color = 'blue';
                option.style.fontWeight = 'bold';
                option.classList.add('correct');
            }

            if (localQuestion && optionText === localQuestion && optionText === answerText) {
                isCorrect = true;
                console.log(`Matched correct answer: ${optionText}`);
            }
        });

        console.log(`Is correct: ${isCorrect}`);

        const img = document.createElement('img');
        img.src = isCorrect ? '/static/Dashboard/정답체크.png' : '/static/Dashboard/틀림체크.png';
        img.alt = isCorrect ? 'Correct' : 'Wrong';
        img.style.position = 'absolute';
        img.style.top = '0';
        img.style.left = '0';
        img.style.width = '80px';
        img.style.height = '80px';
        section.style.position = 'relative';
        section.appendChild(img);
    });
});

function goBack() {
    window.history.back();
}

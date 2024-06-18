function setDifficulty(difficulty, article_code) {
    localStorage.setItem('difficulty', difficulty);
    localStorage.setItem('article_code', article_code);
    window.location.href = `/Difficulty/level1?difficulty=${difficulty}&article_code=${article_code}`;
}

function handleButtonClick(endpoint = null, difficulty = null, article_code = null) {
    if (endpoint) {
        console.log(`handleButtonClick called with endpoint: ${endpoint}, difficulty: ${difficulty}, article_code: ${article_code}`);
        generateArticleAndRedirect(endpoint);
    } else if (difficulty && article_code) {
        console.log(`handleButtonClick called with difficulty: ${difficulty}, article_code: ${article_code}`);
        setDifficulty(difficulty, article_code);
    }
}

function generateArticleAndRedirect(endpoint) {
    console.log(`Generating article with endpoint: ${endpoint}`);
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);
    
    // 로딩창 표시
    document.getElementById('loading').style.display = 'flex';

    fetch(`http://localhost:8000/api/articles/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received data:', data);
        if (data && data.article_code && data.difficulty) {
            localStorage.setItem('article_code', data.article_code);
            localStorage.setItem('difficulty', data.difficulty);
            window.location.href = `/Difficulty/realtime?difficulty=${data.difficulty}&article_code=${data.article_code}`;
        } else {
            console.error('Unexpected response structure:', data);
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        // 로딩창 숨기기
        document.getElementById('loading').style.display = 'none';
        buttons.forEach(button => button.disabled = false);
    });
}

document.getElementById('shortButton').addEventListener('click', function() {
    handleButtonClick(null, 'short', 'ART-001-short');
});

document.getElementById('mediumButton').addEventListener('click', function() {
    handleButtonClick(null, 'middle', 'ART-002-middle');
});

document.getElementById('longButton').addEventListener('click', function() {
    handleButtonClick(null, 'long', 'ART-003-long');
});

document.getElementById('shortRealButton').addEventListener('click', function() {
    handleButtonClick('generate/short');
});

document.getElementById('midRealButton').addEventListener('click', function() {
    handleButtonClick('generate/middle');
});

document.getElementById('longRealButton').addEventListener('click', function() {
    handleButtonClick('generate/long');
});

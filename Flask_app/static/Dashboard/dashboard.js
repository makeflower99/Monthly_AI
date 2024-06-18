document.addEventListener("DOMContentLoaded", function() {
    try {
        const userLevelElement = document.getElementById('userLevelData');
        const scoresElement = document.getElementById('scoresData');
        const summaryTextElement = document.getElementById('summaryTextData');
        const articleCodeElement = document.getElementById('articleCodeData');
        const articleContentElement = document.getElementById('articleContentData');

        if (!userLevelElement || !scoresElement || !summaryTextElement || !articleCodeElement || !articleContentElement) {
            console.error('One or more elements are missing:', {
                userLevelElement,
                scoresElement,
                summaryTextElement,
                articleCodeElement,
                articleContentElement
            });
            return;
        }

        const userLevel = JSON.parse(userLevelElement.textContent);
        const scores = JSON.parse(scoresElement.textContent);
        const summaryText = JSON.parse(summaryTextElement.textContent);
        const articleCode = JSON.parse(articleCodeElement.textContent);
        const articleContent = JSON.parse(articleContentElement.textContent);

        console.log("Article Content:", articleContent);  // 디버깅용 로그
        // 대시보드로 전달되는 데이터 로그 출력
        console.log("User Level:", userLevel);
        console.log("Scores:", scores);
        console.log("Summary Text:", summaryText);
        console.log("Article Code:", articleCode);

        let total_score = scores[0] + scores[1] + scores[2];
        console.log("Total Score:", total_score);  // 디버깅용 로그

        localStorage.setItem('article_code', articleCode);
        localStorage.setItem('article_content', articleContent);  // 추가된 부분

        // 태그 설정
        let tags = [];
        if (articleCode.includes('short')) {
            if (scores[0] < 3) tags.push('개념어');
            if (scores[1] < 3) tags.push('어휘력');
            if (scores[2] < 3) tags.push('독서 기초');
        } else if (articleCode.includes('middle')) {
            if (scores[0] < 4) tags.push('개념어');
            if (scores[1] < 4) tags.push('어휘력');
            if (scores[2] < 4) tags.push('독서 기초');
        } else if (articleCode.includes('long')) {
            if (scores[0] < 5) tags.push('개념어');
            if (scores[1] < 5) tags.push('어휘력');
            if (scores[2] < 5) tags.push('독서 기초');
        }
        localStorage.setItem('tags', JSON.stringify(tags));  // 태그들을 localStorage에 저장

        initDashboard(userLevel, scores, summaryText);  // 수정된 부분
        initPyramid(total_score);
        document.getElementById("total_score").innerText = total_score;

        let keyword_comment = document.getElementById("keyword_comment");
        let voca_comment = document.getElementById("voca_comment");
        let para_comment = document.getElementById("para_comment");

        if (scores[0] === 0) {
            keyword_comment.innerText = "핵심어 파악하는 방법을 다시 공부해보아요. ";
        } else if (scores[0] === 1) {
            keyword_comment.innerText = "핵심어 파악하는 방법을 아직 완벽히 숙지하지는 못한 것 같아요.";
        } else if (scores[0] === 2) {
            keyword_comment.innerText = "핵심어 문제를 비교적 잘하지만 조금 더 집중해서 풀어보아요.";
        } else if (scores[0] === 3) {
            keyword_comment.innerText = "글의 핵심어를 아주 잘 파악하네요.";
        }

        if (scores[1] === 0) {
            voca_comment.innerText = "독서는 어휘력 늘리기에 좋아요.";
        } else if (scores[1] === 1) {
            voca_comment.innerText = "단어의 뜻을 생각해보며 글을 읽어볼까요?";
        } else if (scores[1] === 2) {
            voca_comment.innerText = "어휘력이 어느정도 뛰어나네요.";
        } else if (scores[1] === 3) {
            voca_comment.innerText = "어휘력이 아주 좋네요";
        }

        if (scores[2] === 0) {
            para_comment.innerText = "글의 문단을 요약하는 방법을 다시 공부해보아요.";
        } else if (scores[2] === 1) {
            para_comment.innerText = "글의 문단을 요약하는 방법을 아직 완벽히 숙지하지는 못한 것 같아요.";
        } else if (scores[2] === 2) {
            para_comment.innerText = "글의 문단을 비교적 잘 요약하지만 조금 더 집중해서 요약해보아요.";
        } else if (scores[2] === 3) {
            para_comment.innerText = "문단 요약 능력이 뛰어나네요";
        }

        let user_id = document.getElementById("user_id");
        user_id.innerText = sessionStorage.getItem("user_id");

        const closeButton = document.getElementById('close-button');
        const popup = document.getElementById('popup');
        const popupButtons = document.getElementById('popup-buttons'); // 팝업 버튼 컨테이너를 가져옴
        const yesButton = document.getElementById('yes-button');
        const noButton = document.getElementById('no-button');

        console.log("Close Button:", closeButton); // 디버깅용 로그
        console.log("Popup:", popup); // 디버깅용 로그

        if (closeButton) {
            closeButton.addEventListener('click', function() {
                if (popup) {
                    console.log("Popup should be displayed now."); // 디버깅용 로그
                    popup.classList.remove('hidden'); // hidden 클래스를 제거하여 팝업 표시
                }
            });
        }

        if (yesButton) {
            yesButton.addEventListener('click', function() {
                window.location.href = '/Bulletinboard/Broadening';
            });
        }
        if (noButton) {
            noButton.addEventListener('click', function() {
                localStorage.clear();  // LocalStorage를 초기화
                window.location.href = '/';
            });
        }
    } catch (error) {
        console.error("Error initializing the dashboard:", error);  // 에러 로그 추가
    }
});

function initPyramid(total_score) {
    let element = document.getElementsByClassName("pyramid-level");
    if (total_score === 9)
        element[4].style.backgroundColor = "red";
    else if (total_score === 8)
        element[3].style.backgroundColor = "red";
    else if (total_score === 7)
        element[2].style.backgroundColor = "red";
    else if (total_score === 6)
        element[1].style.backgroundColor = "red";
    else
        element[0].style.backgroundColor = "red";
}

function initDashboard(userLevel, scores, summaryText) {
    // Spider chart
    const ctx = document.getElementById('spiderChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['핵심어요약능력', '어휘능력', '문단요약능력'],
            datasets: [{
                label: '문제풀이결과',
                data: scores,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        display: false
                    },
                    suggestedMin: 0,
                    suggestedMax: 5,
                    ticks: {
                        beginAtZero: true,
                        stepSize: 1, // 정수만 표시되도록 설정
                        callback: function(value) {
                            if (Number.isInteger(value)) {
                                return value;
                            }
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Set summary text
    document.getElementById('summary-text').innerText = summaryText;
}

function openExplanation() {
    const difficulty = localStorage.getItem('difficulty') || 'short';
    const articleCode = localStorage.getItem('article_code');
    window.location.href = `/dashboard/explanation?difficulty=${difficulty}&article_code=${articleCode}`;
}

function openReLecture() {
    const articleContent = localStorage.getItem('article_content');
    const tags = JSON.parse(localStorage.getItem('tags'));  // 태그들을 localStorage에서 가져옴
    const tagString = tags.join(',');  // 태그들을 쉼표로 구분된 문자열로 변환
    window.location.href = `/dashboard/relecture?subject=${encodeURIComponent(articleContent)}&tag=${encodeURIComponent(tagString)}`;
}

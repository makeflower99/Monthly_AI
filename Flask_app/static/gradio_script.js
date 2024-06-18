document.getElementById("generate_article").onclick = function() {
    fetch('http://localhost:8000/api/generate_article', {
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
        if (data && data.title && data.questions) {
            let articleContent = "Title: " + data.title + "\n\n";
            articleContent += "Paragraph 1: " + data.paragraph1 + "\n\n";
            articleContent += "Paragraph 2: " + data.paragraph2 + "\n\n";
            articleContent += "Paragraph 3: " + data.paragraph3 + "\n\n";
            articleContent += "Paragraph 4: " + data.paragraph4 + "\n\n";

            data.questions.forEach((question, index) => {
                articleContent += `Question ${index + 1}: ${question.question}\n`;
                articleContent += `Option 1: ${question.option1}\n`;
                articleContent += `Option 2: ${question.option2}\n`;
                articleContent += `Option 3: ${question.option3}\n`;
                articleContent += `Option 4: ${question.option4}\n`;
                articleContent += `Answer: ${question.answer}\n\n`;
            });
            document.getElementById("article_output").value = articleContent;
        } else {
            console.error('Unexpected response structure:', data);
        }
    })
    .catch(error => console.error('Error:', error));
};

document.getElementById("save_csv").onclick = function() {
    fetch('http://localhost:8000/generate_csv', {
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
        console.log('CSV files created successfully:', data);
        alert("CSV files created successfully");
    })
    .catch(error => console.error('Error:', error));
};

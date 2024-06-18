document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, running loadLectures');
    loadLectures();
});

function loadLectures() {
    const lectureList = document.getElementById('lecture-list');
    const urlParams = new URLSearchParams(window.location.search);
    const subject = urlParams.get('subject');
    const tagString = urlParams.get('tag');
    const tags = tagString ? tagString.split(',').map(tag => tag.trim()) : [];

    console.log('Subject:', subject);
    console.log('Tags:', tags);

    const lectureDataScript = document.getElementById('lecture-data');
    let lectureData;
    try {
        console.log('Lecture Data Script Text Content:', lectureDataScript.textContent.trim());
        let parsedText = JSON.parse(lectureDataScript.textContent.trim());
        if (typeof parsedText === 'string') {
            parsedText = JSON.parse(parsedText);
        }
        lectureData = parsedText;
        console.log('Parsed Lecture Data:', lectureData);
    } catch (e) {
        console.error('Failed to parse lecture data:', e);
        lectureList.innerHTML = '<p>Error: Failed to parse lecture data.</p>';
        return;
    }

    if (!Array.isArray(lectureData)) {
        console.warn('Lecture Data is not an array, converting to array');
        lectureData = [lectureData];
    }

    console.log('Lecture Data:', lectureData);

    if (!subject && tags.length === 0) {
        lectureList.innerHTML = '<p>Please provide either subject or tags in the query parameters.</p>';
        return;
    }

    const filteredLectures = lectureData.filter(lecture => {
        const lectureSubject = lecture['과목'];
        const lectureTags = lecture['태그'] ? lecture['태그'].split(',').map(tag => tag.trim()) : [];
        return (subject && lectureSubject === subject) || tags.some(tag => lectureTags.includes(tag));
    });

    console.log('Filtered Lectures:', filteredLectures);

    if (filteredLectures.length === 0) {
        lectureList.innerHTML = `<p>No lectures found for subject "${subject}" or tags "${tags.join(', ')}".</p>`;
        return;
    }

    const randomLectures = getRandomLectures(filteredLectures, 3);
    randomLectures.forEach(lecture => {
        const lectureDiv = document.createElement('div');
        lectureDiv.className = 'lecture';
        lectureDiv.innerHTML = `<h2>${lecture['강좌명']}</h2><p>과목: ${lecture['과목']}</p><p>강사: ${lecture['강사']}</p>`;
        lectureList.appendChild(lectureDiv);
    });
}

function getRandomLectures(lectures, count) {
    const shuffled = lectures.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function goBack() {
    window.history.back();
}

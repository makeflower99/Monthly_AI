document.getElementById('startButton').addEventListener('click', function() {
    let user_id = document.getElementById("user_id");
    sessionStorage.setItem("user_id", user_id.value);
    window.location.href = '/Difficulty'; // URL 오타 수정
});
document.addEventListener('DOMContentLoaded', function() {
    // Timer logic
    const timerElement = document.getElementById('timer-display');
    if (timerElement) {
        const timeLimit = document.getElementById('timer').getAttribute('data-timelimit');
        let timeRemaining = timeLimit * 60; // convert minutes to seconds

        function updateTimer() {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            if (timeRemaining > 0) {
                timeRemaining--;
            } else {
                clearInterval(timerInterval);
                alert('Time is up!');
                document.getElementById('submit-assessment').click();
            }
        }

        const timerInterval = setInterval(updateTimer, 1000);
    }

    // Save Progress Button
    document.getElementById('save-progress').addEventListener('click', function() {
        const responses = [];
        document.querySelectorAll('textarea').forEach(function(textarea) {
            responses.push({
                question_id: textarea.getAttribute('data-question-id'),
                response_text: textarea.value
            });
        });

        fetch('/save_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: 1,  // Replace with actual student ID
                responses: responses
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        });
    });

    // Submit Assessment Button
    document.getElementById('submit-assessment').addEventListener('click', function() {
        fetch('/submit_assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: 1,  // Replace with actual student ID
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        });
    });
});


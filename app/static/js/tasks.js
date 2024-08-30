document.addEventListener("DOMContentLoaded", function () {
    const taskButtons = document.querySelectorAll('.task-button');
    const doneList = document.querySelector('.done-list');

    taskButtons.forEach(button => {
        const id = button.getAttribute('data-id');
        const link = button.getAttribute('data-link');
        const item = button.closest('.task-item');
        const spinner = button.querySelector('.spinner');

        if (localStorage.getItem(`task-${id}`) === 'claimed') {
            button.classList.add('claimed');
            button.innerHTML = '<i class="fa-sharp fa-solid fa-circle-check"></i>';
            doneList.appendChild(item);
        } else {
            button.addEventListener('click', function (event) {
                window.open(link, '_blank');
                event.preventDefault();

                spinner.style.display = 'block';
                setTimeout(function () {
                    spinner.style.display = 'none';
                    button.classList.remove('start');
                    button.classList.add('claim');
                    button.querySelector('span').textContent = 'Claim';
                }, 4000);

                button.addEventListener('click', function (event) {
                    event.preventDefault();
                    fetch("{% url 'claim_task' %}", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({
                            user_id: '{{ user_id }}',
                            task_id: id,
                        }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            button.classList.add('claimed');
                            button.innerHTML = '<i class="fa-sharp fa-solid fa-circle-check"></i>';
                            doneList.appendChild(item);
                            localStorage.setItem(`task-${id}`, 'claimed');
                        } else {
                            alert(data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
            });
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // Save to favorites
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const affirmationId = this.dataset.affirmationId;
            const btn = this;
            
            fetch("{% url 'save_affirmation' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: `affirmation_id=${affirmationId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-success');
                    btn.textContent = "{% trans 'Saved!' %}";
                } else {
                    btn.textContent = "{% trans 'Already saved' %}";
                }
            });
        });
    });
});
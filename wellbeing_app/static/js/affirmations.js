document.addEventListener('DOMContentLoaded', function() {
    // Save to favorites functionality
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
            .then(response => {
                if (!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(data => {
                if (data.status === 'added') {
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-success');
                    btn.textContent = "{% trans 'Saved!' %}";
                } else if (data.status === 'already_exists') {
                    btn.textContent = "{% trans 'Already saved' %}";
                }
            })
            .catch(error => {
                console.error('Error:', error);
                btn.textContent = "{% trans 'Error saving' %}";
            });
        });
    });
    
    // Generate new affirmations - simple page reload
    document.getElementById('generate-btn').addEventListener('click', function(e) {
        // For better UX, you could add a spinner here
        this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> {% trans "Loading..." %}';
    });
});
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
                    // Show success message
                    const toast = new bootstrap.Toast(document.getElementById('saveToast'));
                    toast.show();
                    
                    // Update button appearance
                    btn.classList.remove('btn-outline-primary');
                    btn.classList.add('btn-success');
                    btn.textContent = "{% trans 'Saved!' %}";
                }
            });
        });
    });

    // Generate new affirmations
    document.getElementById('generate-btn').addEventListener('click', function(e) {
        e.preventDefault();
        
        // Show loading state
        const originalText = this.textContent;
        this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> {% trans "Generating..." %}';
        
        // Reload the affirmations via AJAX
        fetch("{% url 'affirmations' %}", {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            // Replace the affirmations container
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            document.getElementById('affirmations-container').innerHTML = 
                doc.getElementById('affirmations-container').innerHTML;
        })
        .finally(() => {
            // Restore button text
            this.textContent = originalText;
        });
    });
});
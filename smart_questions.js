// Hide findings if last visit was < 30 days ago
document.getElementById('visit-form').addEventListener('change', function(e) {
    const childId = document.getElementById('child_id').value;
    fetch(`/api/last_visit/${childId}`)
      .then(res => res.json())
      .then(data => {
        const diffDays = (new Date() - new Date(data.last_date)) / (1000*60*60*24);
        if (diffDays < 30) {
          document.getElementById('findings').parentElement.style.display = 'none';
        } else {
          document.getElementById('findings').parentElement.style.display = 'block';
        }
      });
  });
  
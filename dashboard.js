// Prepare datasets from injected JSON
const visitsData = JSON.parse('{{ visits|tojson }}');
const vulnsData = JSON.parse('{{ vulns|tojson }}');
const litsData = JSON.parse('{{ lits|tojson }}');

// Home Visits Line Chart
new Chart(document.getElementById('visitsChart'), {
  type: 'line',
  data: {
    labels: visitsData.map(v => v.date),
    datasets: [{
      label: 'Home Visits',
      data: visitsData.map(v => v.count),
      borderColor: 'rgba(75, 192, 192, 1)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderWidth: 2,
      fill: true
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { title: { display: true, text: 'Month' } },
      y: { title: { display: true, text: 'Count' } }
    }
  }
});

// Vulnerability Bar Chart
new Chart(document.getElementById('vulnChart'), {
  type: 'bar',
  data: {
    labels: vulnsData.map(v => v.date),
    datasets: [{
      label: 'Average Vulnerability Score',
      data: vulnsData.map(v => v.score),
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { title: { display: true, text: 'Month' } },
      y: { title: { display: true, text: 'Score' } }
    }
  }
});

// Literacy Bar Chart
new Chart(document.getElementById('litChart'), {
  type: 'bar',
  data: {
    labels: litsData.map(l => l.date),
    datasets: [{
      label: 'Total Ticks',
      data: litsData.map(l => l.ticks),
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { title: { display: true, text: 'Month' } },
      y: { title: { display: true, text: 'Ticks' } }
    }
  }
});





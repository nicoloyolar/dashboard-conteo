const ctxHora = document.getElementById('horaChart').getContext('2d');
        const horas = [];
        const data1kg = [];
        const data500gr = [];
    
        {% for hora, cantidad in productos_por_hora.items() %}
            horas.push('{{ hora }}:00');
            data1kg.push({{ cantidad['1kg'] }});
            data500gr.push({{ cantidad['500gr'] }});
        {% endfor %}
    
        const horaChart = new Chart(ctxHora, {
            type: 'bar',
            data: {
                labels: horas,
                datasets: [
                    {
                        label: '1kg',
                        data: data1kg,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: '500gr',
                        data: data500gr,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: { 
                responsive: true, 
                scales: {
                    x: { title: { display: true, text: 'Hora' }},
                    y: { title: { display: true, text: 'Cantidad' }}
                }
            }
        });
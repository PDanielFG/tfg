<template>
    <div class="w-64 h-64 mx-auto">
        <canvas ref="chartRef"></canvas>
        <div v-if="queries.length === 0" class="text-gray-500 mt-2">
            No hay queries para mostrar.
        </div>

    </div>
</template>


<!-- Componente que mostraremos en la view padre -->
<script>
import { getAPI } from '@/axios-api'

//Cuidado con los imports
import { ref, watch, onMounted, defineComponent } from 'vue'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, DoughnutController } from 'chart.js'

ChartJS.register(DoughnutController, ArcElement, Title, Tooltip, Legend)

export default defineComponent({
    name: 'ChartQueries',


    setup() {
        const chartRef = ref(null)
        const queries = ref([])
        let chartInstance = null

        const fetchQueries = async () => {
            try {
                const res = await getAPI.get('/api/logs/queryList/')
                queries.value = res.data
                renderChart()
            } catch (err) {
                console.error('Error cargando queries:', err)
            }
        }

        const getChartData = () => {

            const errores = queries.value.filter(q => q.was_error).length
            const exitos = queries.value.length - errores

            return {
                labels: ['Correctas', 'Erróneas'],  //El nombre que recibe cada parte 
                datasets: [ //los datso
                    {
                        label: 'Queries',
                        data: [exitos, errores],
                        backgroundColor: ['#42b983', '#e74c3c'],
                        borderWidth: 1
                    }
                ]
            }
        }

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false, // permite que el canvas tome el tamaño del contenedor

            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true, text: 'Queries correctas vs erróneas',
                    font: {
                        size: 15,        // tamaño del texto
                        weight: "bold"   // negrita
                    },
                }
            }
        }

        //Dibujar chart
        const renderChart = () => {
            if (chartInstance) chartInstance.destroy()
            chartInstance = new ChartJS(chartRef.value.getContext('2d'), {
                type: 'doughnut',
                data: getChartData(),
                options: chartOptions
            })
        }

        //montaje grafico
        onMounted(fetchQueries)
        watch(queries, renderChart, { deep: true })

        return { chartRef, queries }
    }
})
</script>

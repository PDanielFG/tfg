<template>
    <div class="w-64 h-64 mx-auto">
        <canvas ref="chartRef"></canvas>
        <div v-if="!queries || queries.length === 0" class="text-gray-500 mt-2">
            No hay queries para mostrar.
        </div>
    </div>
</template>


<!-- Componente que mostraremos en la view padre -->
<script>
//Cuidado con los imports
import { ref, watch, onMounted, defineComponent } from 'vue'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, DoughnutController } from 'chart.js'

ChartJS.register(DoughnutController, ArcElement, Title, Tooltip, Legend)

export default defineComponent({
    name: 'ChartQueries',
    props: {
        //Lo que recibe del padre, USerGraphics.vue, y el tipo de dato
        queries: {
            type: Array,
            default: () => []
        }
    },

    setup(props) {
        const chartRef = ref(null)
        let chartInstance = null

        const getChartData = () => {
            
            const errores = props.queries.filter(q => q.was_error).length   //Una parte del chart
            const exitos = props.queries.length - errores   //l< otra

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
                legend: { position: 'bottom' },
                title: { display: true, text: 'Queries correctas vs erróneas' }
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
        onMounted(renderChart)
        watch(() => props.queries, renderChart, { deep: true })

        return { chartRef }
    }
})
</script>

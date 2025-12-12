<template>
    <div class="w-64 h-64 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="loading" class="text-gray-500 mt-2">
            Cargando...
        </div>

        <div v-if="!loading && totalErrors === 0" class="text-gray-500 mt-2">
            No hay errores para mostrar.
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted, defineComponent, nextTick } from 'vue'
import { getAPI } from '@/axios-api'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, DoughnutController } from 'chart.js'

ChartJS.register(DoughnutController, ArcElement, Title, Tooltip, Legend)

export default defineComponent({
    name: 'ChartErrorTypes',

    //Esto es para saber que usuario consultar en la api, y definimos lo que es, es decir, un string 
    props: {
        username: {
            type: String,
            required: true
        }
    },

    setup(props) {

        //Inicialización previa
        const chartRef = ref(null)  //Referencia al canva del grafico   
        let chartInstance = null    //instancia del grafico

        const loading = ref(true)   //Indica si el usuario sigue cargando
        const syntaxErrors = ref(0)
        const logicErrors = ref(0)
        const totalErrors = ref(0)


        //Funcion para traer datso de la API
        const fetchErrors = async () => {
            loading.value = true
            try {
                const res = await getAPI.get(`/api/logs/user/${props.username}/errors/`)
                syntaxErrors.value = res.data.syntax_errors || 0
                logicErrors.value = res.data.logic_errors || 0
                totalErrors.value = syntaxErrors.value + logicErrors.value


                await nextTick()
                renderChart()
            } catch (err) {
                console.error('Error cargando errores del usuario:', err)
                syntaxErrors.value = 0
                logicErrors.value = 0
                totalErrors.value = 0
            } finally {
                loading.value = false
            }
        }


        //Opciones del grafico
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true,
                    text: 'Errores por tipo (Sintaxis vs Lógicos)',
                    font: { size: 15, weight: 'bold' }
                }
            }
        }

        //Dibuja el chart
        const renderChart = () => {
            if (!chartRef.value) return
            if (chartInstance) chartInstance.destroy()

            chartInstance = new ChartJS(chartRef.value.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Sintaxis', 'Lógicos'],
                    datasets: [{
                        label: 'Errores',
                        data: [syntaxErrors.value, logicErrors.value],
                        backgroundColor: ['#e67e22', '#c0392b'],
                        borderWidth: 1
                    }]
                },
                options: chartOptions
            })
        }

        onMounted(fetchErrors)

        watch(() => props.username, () => {
            fetchErrors()
        })

        return { chartRef, loading, totalErrors }
    }
})
</script>

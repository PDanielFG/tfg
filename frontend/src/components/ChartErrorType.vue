<template>
    <div class="w-64 h-64 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="loading" class="text-gray-500 mt-2">
            Cargando...
        </div>

        <div v-if="!loading && queries.length === 0" class="text-gray-500 mt-2">
            No hay errores para mostrar.
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted, defineComponent } from 'vue'
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

        const queries = ref([])     //Queries del usuario
        const loading = ref(true)   //Indica si el usuario sigue cargando

        //Funcion para traer datso de la API
        const fetchQueries = () => {
            loading.value = true    //Cargando (al principio)

            getAPI.get(`/api/logs/user/${props.username}/`) //Consulta el endpoint de la API
                .then(res => {
                    queries.value = res.data.queries || []  //res-->objeto data-->Los datos (el diccionario que devolvemos en el endpoint de api.py queries-->Una de las propiedades del diccionario, devuelve todas las queries de ese usuario)
                    loading.value = false                   //Deja de cargar porque ya tenemos los datos guardados
                    renderChart()   //Imprime el grafico, llamando a la funcion correspondiente
                })
                //Si hay error vacía queries y oculta el loading 
                .catch(() => {
                    queries.value = []
                    loading.value = false
                })
        }

        const getChartData = () => {
            const syntaxErrors = queries.value.filter(q => q.syntax_error).length   //num queries con syntax_error
            const logicErrors = queries.value.filter(q => q.logic_error).length //num queries con error logico

            //características
            return {
                labels: ['Sintaxis', 'Lógicos'],
                datasets: [
                    {
                        label: 'Tipos de errores',
                        data: [syntaxErrors, logicErrors],
                        backgroundColor: ['#e67e22', '#c0392b'],
                        borderWidth: 1
                    }
                ]
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
                data: getChartData(),
                options: chartOptions
            })
        }

        onMounted(fetchQueries)

        watch(() => props.username, () => {
            fetchQueries()
        })

        return { chartRef, queries, loading }
    }
})
</script>

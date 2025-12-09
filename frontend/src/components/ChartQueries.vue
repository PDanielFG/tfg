<template>
  <div class="w-64 h-64 mx-auto">
    <canvas ref="chartRef"></canvas>

    <div v-if="loading" class="text-gray-500 mt-2">
      Cargando...
    </div>

    <div v-if="!loading && queries.length === 0" class="text-gray-500 mt-2">
      No hay queries para mostrar.
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, defineComponent } from 'vue'
import { getAPI } from '@/axios-api'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, DoughnutController } from 'chart.js'

ChartJS.register(DoughnutController, ArcElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'ChartQueries',

  props: {
    username: {
      type: String,
      required: true
    }
  },

  setup(props) {
    const chartRef = ref(null)
    let chartInstance = null
    const queries = ref([])
    const loading = ref(true)

    // Traer queries de un usuario específico
    const fetchQueries = async () => {
      loading.value = true
      try {
        const res = await getAPI.get(`/api/logs/user/${props.username}/`)
        queries.value = res.data.queries || []
        loading.value = false
        renderChart()
      } catch (err) {
        console.error('Error cargando queries:', err)
        queries.value = []
        loading.value = false
      }
    }

    const getChartData = () => {
      const errores = queries.value.filter(q => q.syntax_error || q.logic_error).length
      const exitos = queries.value.length - errores

      return {
        labels: ['Correctas', 'Erróneas'],
        datasets: [
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
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        title: {
          display: true,
          text: `Queries correctas vs erróneas (${props.username})`,
          font: { size: 15, weight: 'bold' }
        }
      }
    }

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

    watch(() => props.username, fetchQueries)

    return { chartRef, queries, loading }
  }
})
</script>

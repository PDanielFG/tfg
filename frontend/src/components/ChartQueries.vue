<template>
  <div class="w-64 h-64 mx-auto">
    <canvas ref="chartRef"></canvas>

    <div v-if="loading" class="text-gray-500 mt-2">
      Cargando...
    </div>

    <div v-if="!loading && totalQueries === 0" class="text-gray-500 mt-2">
      No hay queries para mostrar.
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, defineComponent, nextTick } from 'vue'
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
    const totalQueries = ref(0)
    const loading = ref(true)

    // Traer queries de un usuario específico
    const fetchQueries = async () => {
      loading.value = true
      try {
        const res = await getAPI.get(`/api/logs/user/${props.username}/query-summary/`)
        const { correctas, erroneas } = res.data
        totalQueries.value = correctas + erroneas
        await nextTick()

        renderChart(correctas, erroneas)
        loading.value=false
      } catch (err) {
        console.error('Error cargando queries:', err)
        // queries.value = []
        totalQueries.value=0
        loading.value = false
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

    const renderChart = (correctas, erroneas) => {
      if (!chartRef.value) return
      if (chartInstance) chartInstance.destroy()
      chartInstance = new ChartJS(chartRef.value.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: ['Correctas', 'Erróneas'],
          datasets: [{
            label: 'Queries',
            data: [correctas, erroneas],
            backgroundColor: ['#42b983', '#e74c3c'],
            borderWidth: 1
          }]
        },
        options: chartOptions
      })
    }

    onMounted(fetchQueries)

    watch(() => props.username, fetchQueries)

    return { chartRef, totalQueries, loading }
  }
})
</script>

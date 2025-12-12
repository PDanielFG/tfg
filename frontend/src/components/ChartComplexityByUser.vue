<template>
  <div class="w-64 h-64 mx-auto">
    <canvas ref="chartRef"></canvas>
    <div v-if="totalQueries === 0" class="text-gray-500 mt-2">
      No hay queries para mostrar.
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, defineComponent } from 'vue'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, DoughnutController } from 'chart.js'
import { getAPI } from '@/axios-api'

ChartJS.register(DoughnutController, ArcElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'ChartUserComplexity',
  props: {
    username: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const chartRef = ref(null)
    const chartInstance = ref(null)
    const totalQueries = ref(0)

    const fetchUserQueries = async () => {
      try {
        const res = await getAPI.get(`/api/logs/user/${props.username}/complexity/`)
        const {total, complejas, simples}=res.data
        totalQueries.value=total

        await nextTick()
        renderChart(complejas, simples)
      } catch (err) {
        console.error('Error cargando queries del usuario:', err)
      }
    }

    const renderChart = (complejas, simples) => {
      if (!chartRef.value) return
      if (chartInstance.value) chartInstance.value.destroy()

      chartInstance.value = new ChartJS(chartRef.value.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: ['Complejas', 'Simples'],
          datasets: [{
            label: 'Consultas',
            data: [complejas, simples],
            backgroundColor: ['#9b59b6', '#f1c40f'] // nuevos colores
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'top' },
            title: {
              display: true,
              text: `Consultas complejas vs simples`,
              font: { size: 15, weight: 'bold' }
            }
          }
        }
      })
    }
    onMounted(fetchUserQueries)

    return { chartRef, totalQueries }
  }
})
</script>

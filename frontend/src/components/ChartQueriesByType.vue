<template>
  <div class="w-full h-96 mx-auto">
    <canvas ref="chartRef"></canvas>

    <div v-if="Object.keys(groupedQueries).length === 0" class="text-gray-500 mt-2">
      No hay datos para mostrar.
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { getAPI } from "@/axios-api";

import {
  Chart as ChartJS,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

export default {
  name: "ChartQueriesByType",

  props: {
    username: { type: String, required: true }
  },

  setup(props) {
    const chartRef = ref(null);
    let chartInstance = null;

    const groupedQueries = ref({});

    const fetchData = async () => {
      try {
        const res = await getAPI.get(`/api/logs/user/${props.username}/`);
        groupedQueries.value = groupByType(res.data.queries || []);
        renderChart();
      } catch (err) {
        console.error("Error:", err);
      }
    };

    function groupByType(queries) {
      const result = {};
      queries.forEach(q => {
        if (q.was_error) return

        const type = q.sql_type || "UNKNOWN";
        result[type] = (result[type] || 0) + 1;
      });
      return result;
    }

    const renderChart = () => {
      if (!chartRef.value) return;
      if (chartInstance) chartInstance.destroy();

      const labels = Object.keys(groupedQueries.value);
      const counts = Object.values(groupedQueries.value);

      chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Queries por tipo SQL",
              data: counts,
              backgroundColor: "#3498db"
            }
          ]
        },
        options: {
          indexAxis: "y", // HORIZONTAL
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              beginAtZero: true,
              title: { display: true, text: "Cantidad" }
            },
            y: {
              title: { display: true, text: "Tipo SQL" }
            }
          }
        }
      });
    };

    onMounted(fetchData);

    return { chartRef, groupedQueries };
  }
};
</script>

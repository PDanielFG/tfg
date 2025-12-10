<template>
  <div class="w-full h-96 mx-auto">
    <canvas ref="chartRef"></canvas>

    <div v-if="!counts || Object.keys(counts).length === 0" class="text-gray-500 mt-2">
      No hay datos para mostrar.
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
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

ChartJS.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default {
  name: "ChartColumnsRef",

  props: {
    username: { type: String, required: true }
  },

  setup(props) {
    const chartRef = ref(null);
    let chartInstance = null;

    // ref con counts y tableMap
    const groupedColumns = ref({ counts: {}, tableMap: {} });

    // computed para exponer counts directamente al template
    const counts = computed(() => groupedColumns.value.counts);

    const fetchData = async () => {
      try {
        const res = await getAPI.get(`/api/logs/user/${props.username}/`);
        groupedColumns.value = groupByColumn(res.data.queries || []);
        renderChart();
      } catch (err) {
        console.error("Error:", err);
      }
    };

    function groupByColumn(queries) {
      const result = {};
      const columnToTable = {};
      queries.forEach(q => {
        if (q.was_error) return;
        if (q.columns && q.columns.length && q.tables && q.tables.length) {
          q.columns.forEach((col, index) => {
            result[col] = (result[col] || 0) + 1;
            columnToTable[col] = q.tables[index] || "unknown";
          });
        }
      });
      return { counts: result, tableMap: columnToTable };
    }

    const renderChart = () => {
      if (!chartRef.value) return;
      if (chartInstance) chartInstance.destroy();

      const { counts, tableMap } = groupedColumns.value;
      const labels = Object.keys(counts);
      const data = Object.values(counts);

      chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
        type: "bar",
        data: { labels, datasets: [{ label: "Columnas más consultadas", data, backgroundColor: "#2ecc71" }] },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const colName = context.label;
                  const tableName = tableMap[colName] || "unknown";
                  return `${colName} (Tabla: ${tableName}) : ${context.raw}`;
                }
              }
            }
          },
          scales: {
            x: { beginAtZero: true, title: { display: true, text: "Cantidad de consultas" } },
            y: { title: { display: true, text: "Columnas" } }
          }
        }
      });
    };

    onMounted(fetchData);

    return { chartRef, groupedColumns, counts };
  }
};
</script>

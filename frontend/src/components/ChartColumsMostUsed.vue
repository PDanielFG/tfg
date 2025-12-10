<template>
    <div class="w-full h-96 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="Object.keys(groupedColumns).length === 0" class="text-gray-500 mt-2">
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
    name: "ChartColumnsRef",

    props: {
        username: { type: String, required: true }
    },

    setup(props) {
        const chartRef = ref(null);
        let chartInstance = null;

        const groupedColumns = ref({});

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
            queries.forEach(q => {
                if (q.columns && q.columns.length) {
                    q.columns.forEach(c => {
                        result[c] = (result[c] || 0) + 1;
                    });
                }
            });
            return result;
        }

        const renderChart = () => {
            if (!chartRef.value) return;
            if (chartInstance) chartInstance.destroy();

            const labels = Object.keys(groupedColumns.value);
            const counts = Object.values(groupedColumns.value);

            chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Columnas más consultadas",
                            data: counts,
                            backgroundColor: "#2ecc71"
                        }
                    ]
                },
                options: {
                    indexAxis: "y", // horizontal
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            title: { display: true, text: "Cantidad de consultas" }
                        },
                        y: {
                            title: { display: true, text: "Columnas" }
                        }
                    }
                }
            });
        };

        onMounted(fetchData);

        return { chartRef, groupedColumns };
    }
};
</script>

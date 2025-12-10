<template>
    <div class="w-full h-96 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="Object.keys(groupedTables).length === 0" class="text-gray-500 mt-2">
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
    name: "ChartTablesRef",

    props: {
        username: { type: String, required: true }
    },

    setup(props) {
        const chartRef = ref(null);
        let chartInstance = null;

        const groupedTables = ref({});

        const fetchData = async () => {
            try {
                const res = await getAPI.get(`/api/logs/user/${props.username}/`);
                groupedTables.value = groupByTable(res.data.queries || []);
                renderChart();
            } catch (err) {
                console.error("Error:", err);
            }
        };

        // Agrupa todas las tablas de todas las queries
        function groupByTable(queries) {
            const result = {};
            queries.forEach(q => {
                if (q.tables && q.tables.length) {
                    q.tables.forEach(t => {
                        result[t] = (result[t] || 0) + 1;
                    });
                }
            });
            return result;
        }

        const renderChart = () => {
            if (!chartRef.value) return;
            if (chartInstance) chartInstance.destroy();

            const labels = Object.keys(groupedTables.value);
            const counts = Object.values(groupedTables.value);

            chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Tablas más consultadas",
                            data: counts,
                            backgroundColor: "#f39c12"
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
                            title: { display: true, text: "Cantidad de consultas" }
                        },
                        y: {
                            title: { display: true, text: "Tablas" }
                        }
                    }
                }
            });
        };

        onMounted(fetchData);

        return { chartRef, groupedTables };
    }
};
</script>

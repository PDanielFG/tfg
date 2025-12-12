<template>
    <div class="w-full h-80 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="finalData.length === 0" class="text-gray-500 mt-2">
            No hay datos para mostrar.
        </div>
    </div>
</template>

<script>
import { ref, watch, onMounted, defineComponent } from "vue";
import { getAPI } from "@/axios-api";

import {
    Chart as ChartJS, BarController, LineController, BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend
} from "chart.js";

ChartJS.register(BarController, LineController, BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend);

export default defineComponent({
    name: "ChartUserConnectionDuration",

    props: {
        username: { type: String, required: true }
    },

    setup(props) {
        const chartRef = ref(null);
        let chartInstance = null;

        const finalData = ref([]);

        // ---------------------------
        // 1. LLAMADA AL ENDPOINT
        // ---------------------------
        const fetchData = async () => {
            try {
                const res = await getAPI.get(`/api/logs/user/${props.username}/sessions-summary/`);

                finalData.value = res.data;
                renderChart()
             
            } catch (err) {
                console.error("Error cargando datos:", err);
                finalData.value=[]
            }
        };

       

        // ---------------------------
        // 3. FORMATEAR DURACIÓN
        // ---------------------------
        function formatDuration(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            let label = "";
            if (hours) label += hours + "h ";
            if (minutes || hours) label += minutes + "m ";
            label += secs + "s";
            return label;
        }

        // ---------------------------
        // 4. PREPARAR CHART.JS
        // ---------------------------
        const getChartData = () => ({
            labels: finalData.value.map(e => e.sessionLabel),
            datasets: [
                {
                    type: "bar",
                    label: "Duración de conexión",
                    data: finalData.value.map(e => e.duration),
                    backgroundColor: "#3498db",
                    yAxisID: "y",
                    order: 1
                },
                {
                    type: "line",
                    label: "Queries por sesión",
                    data: finalData.value.map(e => e.queries),
                    borderColor: "#e74c3c",
                    borderWidth: 2,
                    tension: 0.2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: "#e74c3c",
                    yAxisID: "y2",
                    order: 0
                }
            ]
        });

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Duración" },
                    ticks: {
                        callback: value => formatDuration(value)
                    }
                },
                y2: {
                    beginAtZero: true,
                    position: "right",
                    title: { display: true, text: "Número de queries" },
                    grid: { drawOnChartArea: false }
                },
                x: { title: { display: true, text: "Sesiones" } }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            if (context.dataset.type === "bar") {
                                return `Duración: ${formatDuration(context.raw)}`;
                            }
                            return `Queries: ${context.raw}`;
                        }
                    }
                }
            }
        };

        const renderChart = () => {
            if (!chartRef.value) return;
            if (chartInstance) chartInstance.destroy();

            chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
                data: getChartData(),
                options: chartOptions
            });
        };

        onMounted(fetchData);
        watch(() => props.username, fetchData);

        return { chartRef, finalData };
    }
});
</script>

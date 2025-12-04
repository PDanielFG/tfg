<template>
    <div class="w-full h-72 mx-auto">
        <canvas ref="chartRef"></canvas>

        <div v-if="chartData.length === 0" class="text-gray-500 mt-2">
            No hay datos de conexión para mostrar.
        </div>
    </div>
</template>
<script>
import { ref, watch, onMounted, defineComponent } from "vue";
import { getAPI } from "@/axios-api";

//Importante las importaciones
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

export default defineComponent({
    name: "ChartUserConnectionDuration",

    props: {
        username: {
            type: String,
            required: true
        }
    },

    setup(props) {
        const chartRef = ref(null);
        let chartInstance = null;

        const chartData = ref([]);

        // ---------------------------
        // 1. LLAMADA AL ENDPOINT EXISTENTE USANDO getAPI
        // ---------------------------
        const fetchConnections = async () => {
            try {
                const res = await getAPI.get(`/api/logs/user/${props.username}/`);
                const processed = processConnections(res.data.connections);

                chartData.value = processed;
                renderChart();
            } catch (err) {
                console.error("Error cargando datos:", err);
            }
        };

        // ---------------------------
        // 2. PROCESAR DURACIONES, AGRUPAR POR DÍA Y ORDENAR ASCENDENTE
        // ---------------------------
        function processConnections(connections) {
            const entries = connections.map(c => {
                const day = c.timestamp.split("T")[0]; // YYYY-MM-DD

                let seconds = 0;
                if (c.connection_duration) {
                    const [hh, mm, ss] = c.connection_duration.split(":").map(Number);
                    seconds = hh * 3600 + mm * 60 + ss;
                }

                return { day, duration_seconds: seconds };
            });

            // Agrupar días repetidos sumando duración
            const grouped = {};
            entries.forEach(e => {
                grouped[e.day] = (grouped[e.day] || 0) + e.duration_seconds;
            });

            // Convertir a array y ordenar por fecha ascendente
            return Object.keys(grouped)
                .sort((a, b) => new Date(a) - new Date(b)) // <-- orden ascendente
                .map(day => ({
                    day,
                    duration_seconds: grouped[day]
                }));
        }

        // ---------------------------
        // 3. PREPARAR CHART.JS
        // ---------------------------
        const getChartData = () => ({
            labels: chartData.value.map(e => e.day),
            datasets: [
                {
                    label: "Duración de conexión",
                    data: chartData.value.map(e => e.duration_seconds),
                    backgroundColor: "#3498db"
                }
            ]
        });

        function formatDuration(seconds) {
            if (seconds < 60) return `${seconds}s`;
            if (seconds < 3600) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return `${mins}m ${secs}s`;
            }
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours}h ${mins}m ${secs}s`;
        }

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 30, // espacio superior en píxeles
                    bottom: 0,
                    left: 0,
                    right: 0
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: "Duración de conexión del usuario", // <-- tu título
                    font: {
                        size: 15,        // tamaño del texto
                        weight: "bold"   // negrita
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: "top"
                }
            },

            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Duración" },
                    ticks: {
                        callback: function (value) {
                            return formatDuration(value);
                        }
                    }
                },
                x: {
                    title: { display: true, text: "Dias conectados y duración" }
                }
            }
        };

        const renderChart = () => {
            if (!chartRef.value) return;

            if (chartInstance) chartInstance.destroy();

            chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
                type: "bar",
                data: getChartData(),
                options: chartOptions
            });
        };

        onMounted(fetchConnections);
        watch(() => props.username, fetchConnections);

        return { chartRef, chartData };
    }
});
</script>

<template>
    <div class="w-full h-80 mx-auto">

        <!-- ⭐ NUEVO: Controles -->
        <div class="flex flex-wrap justify-center gap-4 mb-4">
            <select v-model="groupBy" class="border px-3 py-1 rounded shadow-sm">
                <option value="session">Por sesión</option>
                <option value="day">Por día</option>
                <option value="week">Por semana</option>
                <option value="month">Por mes</option>
            </select>

            <!-- ⭐ NUEVO: intervalo de fechas -->
            <input type="date" v-model="fromDate" class="border px-2 py-1 rounded" />
            <input type="date" v-model="toDate" class="border px-2 py-1 rounded" />
        </div>

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

        const groupBy = ref("session");
        const fromDate = ref("");
        const toDate = ref("");

        // ---------------------------
        // 1. LLAMADA AL ENDPOINT
        // ---------------------------
        const fetchData = async () => {
            try {

                const params = {};

                if (groupBy.value !== "session") {
                    params.group_by = groupBy.value;
                }
                if (fromDate.value) params.from = fromDate.value;
                if (toDate.value) params.to = toDate.value;

                const res = await getAPI.get(
                    `/api/logs/user/${props.username}/sessions-summary/`,
                    { params }
                );

                finalData.value = res.data;
                renderChart()

            } catch (err) {
                console.error("Error cargando datos:", err);
                finalData.value = []
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
            labels: finalData.value.map(e => e.label),
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


        const dataLabelsPlugin = {
            id: 'dataLabels',
            afterDatasetsDraw(chart) {
                const ctx = chart.ctx;

                chart.data.datasets.forEach((dataset, datasetIndex) => {
                    if (dataset.type !== 'bar') return;

                    chart.getDatasetMeta(datasetIndex).data.forEach((bar, index) => {
                        const value = dataset.data[index];
                        const label = formatDuration(finalData.value[index].duration); // duración real
                        ctx.save();
                        ctx.fillStyle = '#000';
                        ctx.font = '12px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'bottom';
                        ctx.fillText(label, bar.x, bar.y - 5);
                        ctx.restore();
                    });
                });
            }
        };

        const renderChart = () => {
            if (!chartRef.value) return;
            if (chartInstance) chartInstance.destroy();

            chartInstance = new ChartJS(chartRef.value.getContext("2d"), {
                data: getChartData(),
                options: chartOptions, 
                plugins: [dataLabelsPlugin]
            });
        };

        onMounted(fetchData);

        watch(
            [() => props.username, () => groupBy.value, () => fromDate.value, () => toDate.value],
            fetchData,
            { immediate: true }
        );

        return { chartRef, finalData, groupBy, fromDate, toDate };
    }
});
</script>

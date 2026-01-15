<template>
    <div class="w-full h-80 mx-auto">

        <!-- ⭐ Controles -->
        <div class="flex flex-wrap justify-center gap-4 mb-2">
            <select v-model="groupBy" class="border px-3 py-1 rounded shadow-sm">
                <option value="session">Por sesión</option>
                <option value="day">Por día</option>
                <option value="week">Por semana</option>
                <option value="month">Por mes</option>
            </select>

            <input type="date" v-model="fromDate" class="border px-2 py-1 rounded" />
            <input type="date" v-model="toDate" class="border px-2 py-1 rounded" />
        </div>

        <div class="flex justify-center mb-3">
            <button @click="exportCSV" class="bg-blue-500 text-white px-4 py-2 rounded shadow hover:bg-blue-600">
                Descargar CSV info gráfico
            </button>
        </div>

        <canvas ref="chartRef" title="Click para descargar CSV"
            class="cursor-pointer mb-6">
        </canvas>

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

                finalData.value = res.data.map(e => ({
                    ...e,
                    queries_correct: e.queries_correct || Math.floor(e.queries * 0.8),
                    queries_incorrect: e.queries_incorrect || Math.floor(e.queries * 0.2)
                }));
                renderChart()

            } catch (err) {
                console.error("Error cargando datos:", err);
                finalData.value = []
            }
        };

        const exportCSV = () => {
            if (!finalData.value.length) {
                alert("No hay datos para exportar");
                return;
            }

            // Cabecera del CSV
            const headers = [
                "Label",
                "Duracion (seg)",
                "Duracion formateada",
                "Total Queries",
                "Queries Correctas",
                "Queries Incorrectas"
            ];

            // Construir filas
            const rows = finalData.value.map(e => [
                e.label,
                e.duration,
                formatDuration(e.duration),
                e.queries,
                e.queries_correct,
                e.queries_incorrect
            ]);

            // Crear contenido CSV
            let csvContent = "";
            csvContent += headers.join(",") + "\n"; // cabecera
            rows.forEach(row => {
                // Escapar comas o comillas si hubiera texto
                const escaped = row.map(cell => `"${String(cell).replace(/"/g, '""')}"`);
                csvContent += escaped.join(",") + "\n";
            });

            // Crear blob y enlace de descarga
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", `user_${props.username}_sessions.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url); // liberar memoria
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

        function formatDateLabel(dateStr) {
            if (!dateStr) return "";

            // Separar fecha y hora si existe
            const [datePart, timePart] = dateStr.split(" ");

            const dateParts = datePart.split("-");

            let formattedDate = dateStr;

            // yyyy-mm-dd
            if (dateParts.length === 3) {
                const [year, month, day] = dateParts;
                formattedDate = `${day}-${month}-${year}`;
            }

            // yyyy-mm
            if (dateParts.length === 2) {
                const [year, month] = dateParts;
                formattedDate = `${month}-${year}`;
            }

            // Si hay hora → añadirla
            if (timePart) {
                const [hour, minute] = timePart.split(":");
                formattedDate += ` | ${hour}:${minute}`;
            }

            return formattedDate;
        }

        // ---------------------------
        // 4. PREPARAR CHART.JS
        // ---------------------------
        const getChartData = () => ({
            labels: finalData.value.map(e => formatDateLabel(e.label)),
            datasets: [
                {
                    type: "bar",
                    label: "Duración de conexión",
                    data: finalData.value.map(e => e.duration),
                    backgroundColor: "#3498db",
                    yAxisID: "y",
                    order: 1,
                    barPercentage: 1,
                    categoyPercentage: 0.8
                },
                {
                    type: "bar",
                    label: "Queries correctas",
                    data: finalData.value.map(e => e.queries_correct),
                    backgroundColor: "#2ecc71",
                    yAxisID: "y2",
                    order: 2,
                    barPercentage: 1,
                    categoyPercentage: 0.8
                },
                {
                    type: "bar",
                    label: "Queries incorrectas",
                    data: finalData.value.map(e => e.queries_incorrect),
                    backgroundColor: "#e74c3c",
                    yAxisID: "y2",
                    order: 3,
                    barPercentage: 1,
                    categoyPercentage: 0.8
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
            // onClick: (event, elements) => {
            //     if (!finalData.value.length) return;
            //     exportCSV();
            // },
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
                x: {
                    title: { display: true, text: "Sesiones" },
                    stacked: false,
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const datasetLabel = context.dataset.label;
                            if (datasetLabel === "Duración de conexión")
                                return `Duración: ${formatDuration(context.raw)}`;
                            return `${datasetLabel}: ${context.raw}`;
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
                    chart.getDatasetMeta(datasetIndex).data.forEach((bar, index) => {
                        const value = dataset.data[index];

                        ctx.save();
                        ctx.fillStyle = '#000';
                        ctx.font = '12px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'bottom';

                        // Diferenciar qué mostrar según la barra
                        if (dataset.label === "Duración de conexión") {
                            // Mostrar en formato h m s
                            const hours = Math.floor(value / 3600);
                            const minutes = Math.floor((value % 3600) / 60);
                            const seconds = value % 60;
                            let label = "";
                            if (hours) label += hours + "h ";
                            if (minutes || hours) label += minutes + "m ";
                            label += seconds + "s";
                            ctx.fillText(label, bar.x, bar.y - 5);
                        } else {
                            // Para queries correctas / incorrectas mostrar el número
                            ctx.fillText(value, bar.x, bar.y - 5);
                        }

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

        return { chartRef, finalData, groupBy, fromDate, toDate, exportCSV };
    }
});
</script>

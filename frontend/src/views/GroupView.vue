<template>
    <div class="p-6 bg-gray-100 min-h-screen">
        <h2 class="text-xl font-semibold text-gray-700 mb-6 text-center">
            Estadísticas globales de todos los usuarios
        </h2>

        <div class="mb-10 flex justify-center flex-wrap gap-6">
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartQueriesRef" class="flex-1"></canvas>
            </div>
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartComplexityRef" class="flex-1"></canvas>
            </div>
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartErrorsRef" class="flex-1"></canvas>
            </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <div class="flex flex-wrap justify-center gap-4 mb-4">
                <select v-model="groupBy" class="border px-3 py-1 rounded shadow-sm">
                    <option value="day">Por día</option>
                    <option value="week">Por semana</option>
                    <option value="month">Por mes</option>
                </select>
                <input type="date" v-model="fromDate" class="border px-2 py-1 rounded" />
                <input type="date" v-model="toDate" class="border px-2 py-1 rounded" />
            </div>
            <div class="h-[400px]">
                <canvas ref="chartConnectionsRef" class="h-full w-full"></canvas>
            </div>
        </div>

        <div class="mb-10 flex flex-wrap justify-center gap-6">
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartQueryTypesRef" class="flex-1"></canvas>
            </div>
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartTablesRef" class="flex-1"></canvas>
            </div>
            <div class="flex-1 min-w-[300px] max-w-[400px] h-[350px] bg-white p-4 rounded-lg shadow flex flex-col">
                <canvas ref="chartColumnsRef" class="flex-1"></canvas>
            </div>
        </div>

    </div>
</template>


<script>
import { ref, onMounted, watch, nextTick } from "vue"
import { getAPI } from "@/axios-api"
import {
    Chart as ChartJS,
    Title, Tooltip, Legend,
    ArcElement, DoughnutController,
    BarController, LineController,
    BarElement, LineElement, PointElement,
    CategoryScale, LinearScale
} from "chart.js"

ChartJS.register(
    DoughnutController, ArcElement, Title, Tooltip, Legend,
    BarController, LineController,
    BarElement, LineElement, PointElement,
    CategoryScale, LinearScale
)

export default {
    name: "GlobalStatsView",
    setup() {
        /* DOUGHNUT CHARTS */
        const chartQueriesRef = ref(null)
        const chartComplexityRef = ref(null)
        const chartErrorsRef = ref(null)

        let chartQueriesInstance, chartComplexityInstance, chartErrorsInstance

        const totalQueries = ref(0)
        const totalComplexity = ref(0)
        const totalErrors = ref(0)

        const renderDoughnut = (canvas, instance, labels, data, colors, title) => {
            if (!canvas) return
            if (instance) instance.destroy()
            return new ChartJS(canvas.getContext("2d"), {
                type: "doughnut",
                data: { labels, datasets: [{ data, backgroundColor: colors }] },
                options: { plugins: { legend: { position: "top" }, title: { display: true, text: title } } }
            })
        }

        const fetchQueries = async () => {
            const res = await getAPI.get("/api/logs/global/query-group/")
            const { correctas, erroneas } = res.data
            totalQueries.value = correctas + erroneas
            chartQueriesInstance = renderDoughnut(chartQueriesRef.value, chartQueriesInstance, ["Correctas", "Erróneas"], [correctas, erroneas], ["#42b983", "#e74c3c"], "Queries correctas vs erróneas")
        }

        const fetchComplexity = async () => {
            const res = await getAPI.get("/api/logs/global/complexity-group/")
            const { simples, complejas } = res.data
            totalComplexity.value = simples + complejas
            chartComplexityInstance = renderDoughnut(chartComplexityRef.value, chartComplexityInstance, ["Simples", "Complejas"], [simples, complejas], ["#3498db", "#9b59b6"], "Complejidad de consultas")
        }

        const fetchErrors = async () => {
            const res = await getAPI.get("/api/logs/global/errors-group/")
            const { syntax_errors, logic_errors } = res.data
            totalErrors.value = syntax_errors + logic_errors
            chartErrorsInstance = renderDoughnut(chartErrorsRef.value, chartErrorsInstance, ["Sintaxis", "Lógicos"], [syntax_errors, logic_errors], ["#f39c12", "#e74c3c"], "Tipos de errores")
        }

        /* BARRAS HORIZONTALES */
        const chartQueryTypesRef = ref(null)
        const chartTablesRef = ref(null)
        const chartColumnsRef = ref(null)

        let chartQueryTypesInstance, chartTablesInstance, chartColumnsInstance

        const renderHorizontalBar = (canvas, instance, labels, data, title, color = "#3498db") => {
            if (!canvas) return
            if (instance) instance.destroy()
            return new ChartJS(canvas.getContext("2d"), {
                type: "bar",
                data: { labels, datasets: [{ label: "Número de queries", data, backgroundColor: color }] },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { x: { beginAtZero: true }, y: { beginAtZero: true } },
                    plugins: { legend: { display: false }, title: { display: true, text: title } }
                }
            })
        }

        const fetchQueryTypes = async () => {
            const res = await getAPI.get("/api/logs/global/query-types-group/")
            const labels = res.data.map(e => e.type)
            const data = res.data.map(e => e.count)
            chartQueryTypesInstance = renderHorizontalBar(chartQueryTypesRef.value, chartQueryTypesInstance, labels, data, "Tipos de queries")
        }

        const fetchTables = async () => {
            const res = await getAPI.get("/api/logs/global/tables-group/")
            const labels = res.data.map(e => e.name)
            const data = res.data.map(e => e.count)
            chartTablesInstance = renderHorizontalBar(chartTablesRef.value, chartTablesInstance, labels, data, "Tablas más consultadas", "#2ecc71")
        }

        const fetchColumns = async () => {
            const res = await getAPI.get("/api/logs/global/columns-group/")
            const labels = res.data.map(e => e.name)
            const data = res.data.map(e => e.count)
            chartColumnsInstance = renderHorizontalBar(
                chartColumnsRef.value,
                chartColumnsInstance,
                labels,
                data,
                "Columnas más consultadas",
                "#9b59b6"
            )
        }


        /* GLOBAL SESSIONS */
        const chartConnectionsRef = ref(null)
        let chartConnectionsInstance = null
        const connectionsData = ref([])
        const groupBy = ref("day")
        const fromDate = ref("")
        const toDate = ref("")

        const formatDuration = s => {
            const h = Math.floor(s / 3600)
            const m = Math.floor((s % 3600) / 60)
            return `${h ? h + "h " : ""}${m}m`
        }

        const fetchConnections = async () => {
            const params = { group_by: groupBy.value }
            if (fromDate.value) params.from = fromDate.value
            if (toDate.value) params.to = toDate.value
            const res = await getAPI.get("/api/logs/global/sessions-summary", { params })
            connectionsData.value = res.data
            if (chartConnectionsInstance) chartConnectionsInstance.destroy()
            chartConnectionsInstance = new ChartJS(chartConnectionsRef.value.getContext("2d"), {
                data: {
                    labels: connectionsData.value.map(e => e.label),
                    datasets: [
                        { type: "bar", label: "Duración total", data: connectionsData.value.map(e => e.duration), backgroundColor: "#3498db", yAxisID: "y", order: 1 },
                        { type: "bar", label: "Queries correctas", data: connectionsData.value.map(e => e.queries_correct), backgroundColor: "#2ecc71", yAxisID: "y2", order: 2 },
                        { type: "bar", label: "Queries incorrectas", data: connectionsData.value.map(e => e.queries_incorrect), backgroundColor: "#e74c3c", yAxisID: "y2", order: 3 },
                        { type: "line", label: "Total queries", data: connectionsData.value.map(e => e.queries), borderColor: "#2c3e50", borderWidth: 2, tension: 0.3, pointRadius: 4, yAxisID: "y2", order: 0 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: "Duración" }, ticks: { callback: formatDuration } },
                        y2: { beginAtZero: true, position: "right", title: { display: true, text: "Número de queries" }, grid: { drawOnChartArea: false } }
                    }
                }
            })
        }

        onMounted(() => {
            fetchQueries(); fetchComplexity(); fetchErrors()
            fetchQueryTypes(); fetchTables(); fetchColumns()
            fetchConnections()
        })

        watch([groupBy, fromDate, toDate], fetchConnections)

        return {
            chartQueriesRef, chartComplexityRef, chartErrorsRef,
            chartQueryTypesRef, chartTablesRef, chartColumnsRef,
            chartConnectionsRef,
            totalQueries, totalComplexity, totalErrors,
            connectionsData, groupBy, fromDate, toDate
        }
    }
}
</script>

<template>
    <div class="p-6 bg-gray-100 min-h-screen">
        <h2 class="text-2xl font-bold mb-3 text-gray-700 text-center">Resumen grupal de usuarios</h2>

        <h1 class="text-l font-bold mb-3">
            <router-link
                class="inline-block px-6 py-2 text-white font-semibold rounded-lg shadow-md transition-all duration-200 bg-[#42b983] hover:bg-[#369870] active:scale-95 cursor-pointer"
                :to="{ name: 'GroupGeneral' }">Volver a gráficos</router-link>
        </h1>

        <div class="mb-6 flex justify-center">
            <button @click="downloadCSV"
                class="px-4 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 transition">
                ⬇ Descargar CSV
            </button>
        </div>

        <div v-if="loading" class="text-center text-gray-500">Cargando datos...</div>

        <div v-if="!loading" class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full divide-y divide-gray-200 table-auto">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-2 text-center text-gray-600 font-semibold">Categoría</th>
                        <th class="px-4 py-2 text-center text-gray-600 font-semibold">Elemento</th>
                        <th class="px-4 py-2 text-center text-gray-600 font-semibold">Cantidad</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    <!-- Queries correctas y erróneas -->
                    <tr>
                        <td class="px-4 py-2 font-semibold">Queries</td>
                        <td class="px-4 py-2">Correctas</td>
                        <td class="px-4 py-2 text-center">{{ totals.correct }}</td>
                    </tr>
                    <tr>
                        <td class="px-4 py-2 font-semibold">Queries</td>
                        <td class="px-4 py-2">Erróneas</td>
                        <td class="px-4 py-2 text-center">{{ totals.errors }}</td>
                    </tr>

                    <!-- Complejidad -->
                    <tr>
                        <td class="px-4 py-2 font-semibold">Complejidad</td>
                        <td class="px-4 py-2">Simples</td>
                        <td class="px-4 py-2 text-center">{{ totals.simple }}</td>
                    </tr>
                    <tr>
                        <td class="px-4 py-2 font-semibold">Complejidad</td>
                        <td class="px-4 py-2">Complejas</td>
                        <td class="px-4 py-2 text-center">{{ totals.complex }}</td>
                    </tr>

                    <!-- Errores -->
                    <tr>
                        <td class="px-4 py-2 font-semibold">Errores</td>
                        <td class="px-4 py-2">Sintaxis</td>
                        <td class="px-4 py-2 text-center">{{ totals.syntax }}</td>
                    </tr>
                    <tr>
                        <td class="px-4 py-2 font-semibold">Errores</td>
                        <td class="px-4 py-2">Lógicos</td>
                        <td class="px-4 py-2 text-center">{{ totals.logic }}</td>
                    </tr>

                    <!-- Tipos de queries -->
                    <tr v-for="type in queryTypes" :key="type.type">
                        <td class="px-4 py-2 font-semibold">Tipo de query</td>
                        <td class="px-4 py-2">{{ type.type }}</td>
                        <td class="px-4 py-2 text-center">{{ type.count }}</td>
                    </tr>

                    <!-- Tablas -->
                    <tr v-for="table in tables" :key="table.name">
                        <td class="px-4 py-2 font-semibold">Tabla</td>
                        <td class="px-4 py-2">{{ table.name }}</td>
                        <td class="px-4 py-2 text-center">{{ table.count }}</td>
                    </tr>

                    <!-- Columnas -->
                    <tr v-for="column in columns" :key="column.name">
                        <td class="px-4 py-2 font-semibold">Columna</td>
                        <td class="px-4 py-2">{{ column.name }}</td>
                        <td class="px-4 py-2 text-center">{{ column.count }}</td>
                    </tr>

                    <!-- Conexiones y duración -->
                    <tr v-for="session in sessions" :key="session.label">
                        <td class="px-4 py-2 font-semibold">Conexiones</td>
                        <td class="px-4 py-2">{{ session.label }}</td>
                        <td class="px-4 py-2 text-center">
                            {{ session.duration }}s (Correctas: {{ session.queries_correct }}, Erróneas: {{
                                session.queries_incorrect }})
                        </td>
                    </tr>
                </tbody>

            </table>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from "vue"
import { getAPI } from "@/axios-api"

export default {
    name: "GroupTable",
    setup() {
        const loading = ref(true)

        const totals = ref({
            correct: 0,
            errors: 0,
            simple: 0,
            complex: 0,
            syntax: 0,
            logic: 0
        })

        const queryTypes = ref([])
        const tables = ref([])
        const columns = ref([])
        const sessions = ref([])

        const fetchTotals = async () => {
            // Queries correctas/erróneas
            const queriesRes = await getAPI.get("/api/logs/global/query-group/")
            totals.value.correct = queriesRes.data.correctas
            totals.value.errors = queriesRes.data.erroneas

            // Complejidad
            const compRes = await getAPI.get("/api/logs/global/complexity-group/")
            totals.value.simple = compRes.data.simples
            totals.value.complex = compRes.data.complejas

            // Errores
            const errorsRes = await getAPI.get("/api/logs/global/errors-group/")
            totals.value.syntax = errorsRes.data.syntax_errors
            totals.value.logic = errorsRes.data.logic_errors

            // Tipos de queries
            const typesRes = await getAPI.get("/api/logs/global/query-types-group/")
            queryTypes.value = typesRes.data

            // Tablas
            const tablesRes = await getAPI.get("/api/logs/global/tables-group/")
            tables.value = tablesRes.data

            // Columnas
            const columnsRes = await getAPI.get("/api/logs/global/columns-group/")
            columns.value = columnsRes.data

            // Conexiones
            const sessionsRes = await getAPI.get("/api/logs/global/sessions-summary")
            sessions.value = sessionsRes.data

            loading.value = false
        }

        const downloadCSV = () => {
            const rows = []

            // Totales
            rows.push(["Queries", "Correctas", totals.value.correct])
            rows.push(["Queries", "Erroneas", totals.value.errors])
            rows.push(["Complejidad", "Simples", totals.value.simple])
            rows.push(["Complejidad", "Complejas", totals.value.complex])
            rows.push(["Errores", "Sintaxis", totals.value.syntax])
            rows.push(["Errores", "Logicos", totals.value.logic])

            // Tipos
            queryTypes.value.forEach(q => rows.push(["Tipo de query", q.type, q.count]))
            tables.value.forEach(t => rows.push(["Tabla", t.name, t.count]))
            columns.value.forEach(c => rows.push(["Columna", c.name, c.count]))
            sessions.value.forEach(s => rows.push(["Conexión", s.label, `${s.duration}s (Correctas: ${s.queries_correct}, Erróneas: ${s.queries_incorrect})`]))

            const csvContent = "data:text/csv;charset=utf-8," +
                rows.map(e => e.join(",")).join("\n")
            const encodedUri = encodeURI(csvContent)
            const link = document.createElement("a")
            link.setAttribute("href", encodedUri)
            link.setAttribute("download", "group_summary.csv")
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
        }

        onMounted(() => {
            fetchTotals()
        })

        return { totals, queryTypes, tables, columns, sessions, loading, downloadCSV }
    }
}
</script>

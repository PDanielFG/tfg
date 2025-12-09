<template>
    <div class="p-6 bg-gray-100 min-h-screen">
        <div class="mb-8 flex justify-center flex-wrap gap-6">
            <!-- Gráfico de queries correctas vs erróneas -->
            <div class="flex-1 min-w-[300px] max-w-[400px] bg-white p-4 rounded-lg shadow">
                <ChartQueries :username="selectedUser" />
            </div>

            <div class="flex-1 min-w-[300px] max-w-[400px] bg-white p-4 rounded-lg shadow">
                <ChartErrorType :username="selectedUser" /> <!--Parametro dinamico-->
            </div>

            <!-- Gráfico de consultas complejas vs sencillas por usuario -->
            <div class="flex-1 min-w-[300px] max-w-[400px] bg-white p-4 rounded-lg shadow">
                <ChartComplexityByUser :username="selectedUser" />
            </div>
        </div>

        <!-- Gráfico de duración de conexión del usuario -->
        <div class="mb-8">
            <ChartUserConnectionDuration :username="selectedUser" />
        </div>
    </div>
</template>

<script>
import { getAPI } from '@/axios-api'
import ChartComplexityByUser from '@/components/ChartComplexityByUser.vue';
import ChartQueries from '@/components/ChartQueries.vue'
import ChartUserConnectionDuration from '@/components/ChartUserConnectionDuration.vue'
import ChartErrorType from '@/components/ChartErrorType.vue';

export default {
    name: 'UserProfile',
    components: { ChartQueries, ChartUserConnectionDuration, ChartComplexityByUser, ChartErrorType },
    data() {
        return {
            usuario: {},
            queries: [],
            conexiones: [],
            selectedUser: this.$route.params.username, // Para el gráfico de conexiones
            error: null
        }
    },
    created() {
        const username = this.$route.params.username

        getAPI.get(`/api/logs/user/${username}/`)
            .then(res => {
                this.usuario = {
                    user: res.data.user,
                    last_connected: res.data.last_connected
                }
                this.queries = res.data.queries
                this.conexiones = res.data.connections
            })
            .catch(() => {
                this.error = "No se pudieron cargar los datos del usuario"
            })
    },
    methods: {
        formatDate(dateStr) {
            if (!dateStr) return '-'
            return new Intl.DateTimeFormat('es-ES', {
                dateStyle: 'short',
                timeStyle: 'medium',
                timeZone: 'UTC'
            }).format(new Date(dateStr))
        },
        formatDuration(duration) {
            if (!duration) return '-'
            const [h, m, s] = duration.split(':')
            return `${h}h ${m}m ${s}s`
        }
    }
}
</script>

<template>
    <div class="p-6 bg-gray-100 min-h-screen">
        <h1 v-if="!queries || queries.length === 0" class="text-2xl font-bold mb-6">
            <router-link
                class="inline-block px-6 py-2 text-white font-semibold rounded-lg shadow-md transition-all duration-200 bg-[#42b983] hover:bg-[#369870] active:scale-95 cursor-pointer"
                :to="`/users/${$route.params.username}/graphics`">
                Ver estadísticas
            </router-link>
        </h1>


        <!-- Aquí agregamos el gráfico -->
        <div class="mb-8">
            <ChartQueries :queries="queries" />
            <ChartUserConnectionDuration :username="selectedUser" />

        </div>
    </div>

</template>
<script>
import { getAPI } from '@/axios-api'
import ChartQueries from '@/components/ChartQueries.vue'
import ChartUserConnectionDuration from '@/components/ChartUserConnectionDuration.vue'

export default {
    name: 'UserProfile',
    components: { ChartQueries, ChartUserConnectionDuration },
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

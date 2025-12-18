<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h1 class="text-2xl font-bold mb-6">
      <router-link
        class="inline-block px-6 py-2 text-white font-semibold rounded-lg shadow-md transition-all duration-200 bg-[#42b983] hover:bg-[#369870] active:scale-95 cursor-pointer"
        :to="{ name: 'UserGraphics', params: { username: $route.params.username } }">Ver estadísticas</router-link>
    </h1>

    <div class="mb-4">
      <span class="font-semibold">Última conexión: </span>
      <span>{{ formatDate(usuario?.last_connected) }}</span>
    </div>

    <h2 class="text-xl font-semibold mt-6 mb-4">
      Queries realizadas: <span class="text-gray-600">{{ queries.length }}</span>
    </h2>

    <div class="mb-4">
      <label class="block text-sm font-semibold text-gray-700">Tipo de consulta</label>
      <select v-model="filterQueryType" @change="applyQueryFilter" class="px-3 py-2 border rounded-lg shadow-sm">
        <option value="">Todas</option>
        <option value="SELECT">SELECT</option>
        <option value="INSERT">INSERT</option>
        <option value="CREATE TABLE">CREATE TABLE</option>
        <option value="SUBQUERY_NESTED">Subconsulta anidada</option>
        <option value="SUBQUERY_CORRELATED">Subconsulta correlacionada</option>
      </select>
    </div>

    <div v-if="queries.length === 0" class="mt-2 text-gray-600">
      Este usuario no tiene queries registradas.
    </div>

    <div v-if="queries.length" class="overflow-x-auto bg-white rounded-lg shadow">
      <table class="min-w-full divide-y divide-gray-200 table-fixed">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Timestamp</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">User</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Id usuario</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Query</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Error</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Mensaje de error</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="q in queries" :key="q.id" :class="{
            'hover:bg-gray-50': true,
            'bg-red-100 text-red-800': q.was_error === true,
            'bg-green-100 text-green-800': q.was_error === false
          }">
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ formatDate(q.timestamp) }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ q.user_host || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ q.thread_id || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.query || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.was_error === true ? 'Sí' : 'No'
            }}
            </td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.error_message || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h2 class="text-xl font-semibold mt-6 mb-4">Conexiones realizadas:</h2>

    <div v-if="conexiones.length === 0" class="mt-2 text-gray-600">
      Este usuario no tiene conexiones registradas.
    </div>

    <div v-if="conexiones.length" class="overflow-x-auto bg-white rounded-lg shadow mb-6">
      <table class="min-w-full divide-y divide-gray-200 table-fixed">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Timestamp</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">User</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Id usuario</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Duracion</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="c in conexiones" :key="c.id" class="hover:bg-gray-50">
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ formatDate(c.timestamp) }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ c.user_host || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ c.thread_id || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ formatDuration(c.connection_duration)
            }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { getAPI } from '@/axios-api';

export default {
  name: 'UserProfile',
  data() {
    return {
      usuario: {},
      queries: [],
      queriesOriginal: [], // ⭐ NUEVO: guardar todas las queries originales
      conexiones: [],
      error: null,
      filterQueryType: "",

    };
  },

  created() {
    const username = this.$route.params.username;

    getAPI.get(`/api/logs/user/${username}/`)
      .then(res => {
        this.usuario = {
          user: res.data.user,
          last_connected: res.data.last_connected
        };
        this.queriesOriginal = res.data.queries; 
        this.queries = [...this.queriesOriginal]; 
        this.conexiones = res.data.connections; //Llamamos a connections en vez de conexiones porque connections en la propiedad del backend, del diccionario

        this.applyQueryFilter(); 

      })
      .catch(() => {
        this.error = "No se pudieron cargar los datos del usuario";
      });
  },

  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Intl.DateTimeFormat('es-ES', {
        dateStyle: 'short',
        timeStyle: 'medium',
        timeZone: 'UTC'
      }).format(new Date(dateStr));
    },

    formatDuration(duration) {
      if (!duration) return '-';

      // duration viene como "HH:MM:SS" desde Django
      const [h, m, s] = duration.split(':');
      return `${h}h ${m}m ${s}s`;
    },

    applyQueryFilter() {
      let filtered = [...this.queriesOriginal];

      if (this.filterQueryType) {
        filtered = filtered.filter(q => {
          const queryUpper = (q.query || "").toUpperCase();

          if (this.filterQueryType === "SELECT") {
            return queryUpper.startsWith("SELECT") && !this.isSubquery(queryUpper);
          }
          if (this.filterQueryType === "INSERT") return queryUpper.startsWith("INSERT");
          if (this.filterQueryType === "CREATE TABLE") return queryUpper.startsWith("CREATE TABLE");
          if (this.filterQueryType === "SUBQUERY_NESTED") return this.isNestedSubquery(queryUpper);
          if (this.filterQueryType === "SUBQUERY_CORRELATED") return this.isCorrelatedSubquery(queryUpper);

          return true;
        });
      }

      this.queries = filtered;
    },

    // ⭐ NUEVO: helpers para subconsultas
    isSubquery(query) {
      return /\(\s*SELECT\s+/i.test(query); // Detecta subconsultas
    },

    isNestedSubquery(query) {
      return /\(\s*SELECT\s+.*\)/i.test(query); // Subconsulta anidada simple
    },

    isCorrelatedSubquery(query) {
      return /\(\s*SELECT\s+.*FROM\s+\w+\s+.*\.\w+/i.test(query); // Subconsulta correlacionada simplificada
    }
  }
}
</script>

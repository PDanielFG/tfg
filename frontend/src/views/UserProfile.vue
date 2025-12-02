<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h1 class="text-2xl font-bold mb-6">
      Vista de {{ usuario?.user }}
    </h1>

    <div class="mb-4">
      <span class="font-semibold">Última conexión:</span>
      <span>{{ formatDate(usuario?.last_connected) }}</span>
    </div>

    <h2 class="text-xl font-semibold mt-6 mb-4">Queries realizadas:</h2>

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
          <tr 
            v-for="q in queries" 
            :key="q.id" 
            :class="{
              'hover:bg-gray-50': true,
              'bg-red-100 text-red-800': q.was_error === true,
              'bg-green-100 text-green-800': q.was_error === false
            }"
          >
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ formatDate(q.timestamp) }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ q.user_host || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ q.thread_id || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.query || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.was_error === true ? 'Sí' : 'No' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ q.error_message || '-' }}</td>
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
      error: null
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
        this.queries = res.data.queries;
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
    }
  }
}
</script>

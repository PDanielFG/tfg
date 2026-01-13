<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">Listado de Logs MySQL</h2>

    <div v-if="error" class="mb-4 p-2 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-if="logs.length === 0" class="text-gray-500">No hay registros disponibles.</div>
    <div class="mb-4 text-gray-700 font-semibold">
      Total de logs: {{ totalLogs }}
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 py-4">
      <button class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50" :disabled="currentPage === 1"
        @click="currentPage--">
        Anterior
      </button>

      <span class="font-semibold">
        Página {{ currentPage }} de {{ totalPages }}
      </span>

      <button class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
        :disabled="currentPage === totalPages" @click="currentPage++">
        Siguiente
      </button>
    </div>


    <div v-if="logs.length" class="overflow-x-auto bg-white rounded-lg shadow">
      <table class="min-w-full divide-y divide-gray-200 table-fixed">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Timestamp</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">User</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Command</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Query</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Error</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Mensaje de error</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Error sintáctico</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Error lógico</th>

          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="log in paginatedLogs" :key="log.id"
            :class="{ 'hover:bg-gray-50': true, 'bg-red-100 text-red-800': log.was_error === true, 'bg-green-100 text-green-800': log.was_error === false }">
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ formatDate(log.timestamp) }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ log.user_host || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center whitespace-nowrap">{{ log.command_type || '-' }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ log.query || '-' }}</td>
            <!--si log.was_error es true pone si (que es la primera opcion antes del ?), si es false pone la segunda-->
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl"> {{ log.was_error === true ? 'Sí' :
              'No'
            }}</td>
            <td class="px-4 py-2 text-gray-700 text-center break-words max-w-xl">{{ log.error_message || '-' }}</td>

            <td class="px-4 py-2 text-center">
              <span v-if="log.syntax_error" class="text-red-600 font-semibold">
                Error Sintaxis
              </span>
              <span v-else>-</span>
            </td>

            <td class="px-4 py-2 text-center">
              <span v-if="log.logic_error" class="text-red-600 font-semibold">
                Error Lógico
              </span>
              <span v-else>-</span>
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
  name: 'logsList',

  data() {
    return {
      logs: [],
      logsOriginal: [],
      error: null,
      currentPage: 1,
      pageSize: 50
    }
  },
  created() {
    this.listarLogs();
  },
  computed: {
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.logs.slice(start, end);
    },

    totalPages() {
      return Math.ceil(this.logs.length / this.pageSize);
    },

    totalLogs() {
      return this.logsOriginal.length;
    }
  },

  methods: {
    async listarLogs() {
      try {
        const res = await getAPI.get('/api/logs/queryList/'); // 🔹 agregar res
        const filteredLogs = res.data.filter(log => log.user_host && !log.user_host.startsWith('test@'));
        this.logsOriginal = filteredLogs; // guardar todos los logs originales
        this.logs = [...filteredLogs];    // tabla actual
        this.currentPage = 1;

      } catch (err) {
        console.error(err);
        this.error = 'Error al cargar los logs';
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Intl.DateTimeFormat('es-ES', {
        dateStyle: 'short',
        timeStyle: 'medium',
        timeZone: 'UTC'   // Evita la conversión automática
      }).format(new Date(dateStr));
    }

  }
}
</script>

<style scoped>
/* Limitar ancho de columna Query y permitir saltos de línea */
td.break-words {
  max-width: 600px;
  word-wrap: break-word;
}
</style>

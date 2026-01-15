<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">Usuarios Conectados</h2>

    <button @click="downloadCSV"
      class="px-4 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 transition mb-6">
      ⬇ Descargar todo. CSV
    </button>

    <div v-if="error" class="mb-4 p-2 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <!-- Filtros -->
    <div class="mb-6 flex flex-wrap items-end justify-center gap-4">
      <div>
        <label class="block text-sm font-semibold text-gray-700">Usuario</label>
        <input v-model="filterUsername" @input="applyFilters" type="text" placeholder="Buscar usuario"
          class="px-3 py-2 border rounded-lg shadow-sm focus:ring focus:ring-blue-300" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700">Desde</label>
        <input v-model="filterFromDate" @change="applyFilters" type="date"
          class="px-3 py-2 border rounded-lg shadow-sm" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700">Hasta</label>
        <input v-model="filterToDate" @change="applyFilters" type="date"
          class="px-3 py-2 border rounded-lg shadow-sm" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700">Últimos X días</label>
        <input v-model.number="filterLastDays" @input="listarUsuarios" type="number" min="1" placeholder="Ej: 7"
          class="px-3 py-2 border rounded-lg shadow-sm w-32" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700">Mínimo consultas</label>
        <input v-model.number="filterMinQueries" @input="applyFilters" type="number" min="1" placeholder="Ej: 5"
          class="px-3 py-2 border rounded-lg shadow-sm w-32" />
      </div>
    </div>

    <!-- Media -->
    <div class="mb-4 text-center text-gray-700">
      <span class="font-semibold">Media grupal de consultas:</span>
      <span class="ml-2 text-blue-600 font-bold">{{ averageQueries.toFixed(2) }}</span>
      <span class="ml-6 font-semibold">Media grupal de conexiones:</span>
      <span class="ml-2 text-purple-600 font-bold">{{ averageConnections.toFixed(2) }}</span>
    </div>

    <!-- Ordenación -->
    <div class="mb-4 flex items-center justify-center gap-4">
      <label class="text-gray-700 font-semibold">Ordenar por:</label>
      <select v-model="sortOption" @change="applyFilters"
        class="px-3 py-2 border rounded-lg bg-white shadow-sm focus:ring focus:ring-blue-300">
        <option value="az">Usuario A → Z</option>
        <option value="za">Usuario Z → A</option>
        <option value="queries_desc">Más consultas</option>
        <option value="queries_asc">Menos consultas</option>
        <option value="connections_desc">Más conexiones</option>
        <option value="connections_asc">Menos conexiones</option>
        <option value="recent">Última conexión (más reciente)</option>
        <option value="oldest">Última conexión (más antigua)</option>
      </select>
    </div>

    <div v-if="users.length" class="overflow-x-auto bg-white rounded-lg shadow">
      <table class="min-w-full table-fixed divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="w-1/2 px-4 py-3 text-center text-gray-600 font-semibold uppercase">Usuario</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Conexiones</th>
            <th class="px-4 py-3 text-center text-gray-600 font-semibold uppercase">Consultas</th>
            <th class="w-1/2 px-4 py-3 text-center text-gray-600 font-semibold uppercase">Última Conexión</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="(user, index) in paginatedUsers" :key="user.user" class="hover:bg-gray-50 cursor-pointer"
            @click="goToUser(user.user)">
            <td class="px-4 py-2 text-center">
              <span v-if="isQueryRanking">
                {{ getRanking((currentPage - 1) * pageSize + index) }}º -
              </span>
              {{ user.user }}
            </td>

            <td class="px-4 py-2 text-center font-semibold"
              :class="isAboveAverageConnections(user) ? 'text-green-600' : 'text-red-600'">
              {{ user.connections_count }}
            </td>

            <td class="px-4 py-2 text-center font-semibold"
              :class="isAboveAverage(user) ? 'text-green-600' : 'text-red-600'">
              {{ user.queries_count }}
            </td>

            <td class="px-4 py-2 text-center">
              {{ formatDate(user.last_connected) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 py-4">
      <button class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50" :disabled="currentPage === 1"
        @click="currentPage--">
        Anterior
      </button>
      <span class="font-semibold">Página {{ currentPage }} de {{ totalPages }}</span>
      <button class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
        :disabled="currentPage === totalPages" @click="currentPage++">
        Siguiente
      </button>
    </div>
  </div>
</template>

<script>
import { getAPI } from '@/axios-api';

export default {
  name: 'connectedUsers',
  data() {
    return {
      users: [],
      usersOriginal: [],
      error: null,
      sortOption: 'az',
      filterUsername: '',
      filterFromDate: '',
      filterToDate: '',
      filterMinQueries: null,
      filterLastDays: null,
      currentPage: 1,
      pageSize: 25,
      csvUrl: (process.env.VUE_APP_API_URL || "http://localhost:8000") + "/api/logs/export/csv",
    }
  },
  created() {
    this.listarUsuarios();
  },
  computed: {
    averageQueries() {
      if (!this.usersOriginal.length) return 0;
      const total = this.usersOriginal.reduce((sum, u) => sum + u.queries_count, 0);
      return total / this.usersOriginal.length;
    },
    averageConnections() {
      if (!this.usersOriginal.length) return 0;
      const total = this.usersOriginal.reduce((sum, u) => sum + u.connections_count, 0);
      return total / this.usersOriginal.length;
    },
    isQueryRanking() {
      return this.sortOption === "queries_desc" || this.sortOption === "queries_asc";
    },
    totalUsers() { return this.usersOriginal.length },
    totalFilteredUsers() { return this.users.length },
    paginatedUsers() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.users.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.users.length / this.pageSize);
    }
  },
  methods: {
    async listarUsuarios() {
      try {
        const params = {};
        if (this.filterLastDays) params.days = this.filterLastDays;
        const res = await getAPI.get('/api/logs/connected-users-summary/', { params });
        this.usersOriginal = res.data.filter(u => u.user.toLowerCase() !== 'test');
        this.applyFilters();
      } catch (err) {
        console.error(err);
        this.error = 'Error al cargar usuarios conectados';
      }
    },
    applyFilters() {
      let filtered = [...this.usersOriginal];
      if (this.filterUsername) {
        const search = this.filterUsername.toLowerCase();
        filtered = filtered.filter(u => u.user.toLowerCase().includes(search));
      }
      if (this.filterFromDate) {
        const from = new Date(this.filterFromDate);
        filtered = filtered.filter(u => new Date(u.last_connected) >= from);
      }
      if (this.filterToDate) {
        const to = new Date(this.filterToDate); to.setHours(23,59,59,999);
        filtered = filtered.filter(u => new Date(u.last_connected) <= to);
      }
      if (this.filterMinQueries) {
        filtered = filtered.filter(u => u.queries_count >= this.filterMinQueries);
      }
      this.users = filtered;
      this.sortUsers();
      this.currentPage = 1;
    },
    sortUsers() {
      if (this.sortOption === "az") this.users.sort((a,b) => a.user.localeCompare(b.user));
      else if (this.sortOption === "za") this.users.sort((a,b) => b.user.localeCompare(a.user));
      else if (this.sortOption === "recent") this.users.sort((a,b) => new Date(b.last_connected) - new Date(a.last_connected));
      else if (this.sortOption === "oldest") this.users.sort((a,b) => new Date(a.last_connected) - new Date(b.last_connected));
      else if (this.sortOption === "queries_desc") this.users.sort((a,b) => b.queries_count - a.queries_count);
      else if (this.sortOption === "queries_asc") this.users.sort((a,b) => a.queries_count - b.queries_count);
      else if (this.sortOption === "connections_desc") this.users.sort((a,b) => b.connections_count - a.connections_count);
      else if (this.sortOption === "connections_asc") this.users.sort((a,b) => a.connections_count - b.connections_count);
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Intl.DateTimeFormat('es-ES', { dateStyle: 'short', timeStyle: 'medium', timeZone: 'UTC' }).format(new Date(dateStr));
    },
    getRanking(index) { return index + 1 },
    downloadCSV() { window.open(this.csvUrl, "_blank") },
    isAboveAverage(user) { return user.queries_count >= this.averageQueries },
    isAboveAverageConnections(user) { return user.connections_count >= this.averageConnections },
    goToUser(username) { this.$router.push({ name:'UserProfile', params:{username} }) },
  }
}
</script>

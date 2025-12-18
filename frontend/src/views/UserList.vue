<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">Usuarios Conectados</h2>

    <div v-if="error" class="mb-4 p-2 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <!-- ⭐ NUEVO: Filtros -->
    <div class="mb-6 flex flex-wrap items-end justify-center gap-4">
      <div>
        <label class="block text-sm font-semibold text-gray-700 font-semibold">Usuario</label>
        <input v-model="filterUsername" @input="applyFilters" type="text" placeholder="Buscar usuario"
          class="px-3 py-2 border rounded-lg shadow-sm focus:ring focus:ring-blue-300" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 font-semibold">Desde</label>
        <input v-model="filterFromDate" @change="applyFilters" type="date"
          class="px-3 py-2 border rounded-lg shadow-sm" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700 font-semibold">Hasta</label>
        <input v-model="filterToDate" @change="applyFilters" type="date"
          class="px-3 py-2 border rounded-lg shadow-sm" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-gray-700">Últimos X días</label>
        <input v-model.number="filterLastDays" @input="listarUsuarios" type="number" min="1" placeholder="Ej: 7"
          class="px-3 py-2 border rounded-lg shadow-sm w-32" />
      </div>

      <!-- Filtrar por mínimo de consultas -->
      <div>
        <label class="block text-sm font-semibold text-gray-700">Mínimo consultas</label>
        <input v-model.number="filterMinQueries" @input="applyFilters" type="number" min="1" placeholder="Ej: 5"
          class="px-3 py-2 border rounded-lg shadow-sm w-32" />
      </div>
    </div>

    <!-- Controles de ordenación -->
    <div class="mb-4 flex items-center justify-center gap-4">
      <label class="text-gray-700 font-semibold">Ordenar por:</label>
      <select v-model="sortOption" @change="applyFilters"
        class="px-3 py-2 border rounded-lg bg-white shadow-sm focus:ring focus:ring-blue-300">
        <option value="az">Usuario A → Z</option>
        <option value="za">Usuario Z → A</option>
        <option value="queries_desc">RANKING - Más consultas</option>
        <option value="queries_asc">RANKING - Menos consultas</option>
        <option value="recent">Última conexión (más reciente)</option>
        <option value="oldest">Última conexión (más antigua)</option>
      </select>
    </div>

    <div v-if="users.length === 0 && !error" class="text-gray-500">
      No hay usuarios conectados.
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
          <!--Con router link hacemos toda la fila clickable, hacia la nueva vista, eliminamos la etiqeuta tr
          Con el parametro dinámico param, genera un endpoint nuevo usando el ednpoint que acabamos de crear en router index.js
          con name UserProfile/parametro dincamico-->
          <router-link v-for="(user, index) in users" :key="user.user"
            :to="{ name: 'UserProfile', params: { username: user.user } }" class="flex hover:bg-gray-50 cursor-pointer"
            style="display: table-row;">
            <td class="px-4 py-2 text-gray-700 text-center">
              <span v-if="isQueryRanking">
                {{ getRanking(index) }}º -
              </span>
              {{ user.user }}
            </td>
            <td class="px-4 py-2 text-gray-700 text-center">{{ user.connections_count }}</td>
            <td class="px-4 py-2 text-gray-700 text-center">{{ user.queries_count }}</td>
            <td class="px-4 py-2 text-gray-700 text-center">{{ formatDate(user.last_connected) }}</td>
          </router-link>
        </tbody>
      </table>
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
      sortOption: 'az', // opción por defecto


      filterUsername: '',
      filterFromDate: '',
      filterToDate: '',

      filterMinQueries: null,  // Número mínimo de consultas
      filterLastDays: null     // Últimos X días
    }
  },
  created() {
    this.listarUsuarios();
  },
  computed: {
    isQueryRanking() {
      return (
        this.sortOption === "queries_desc" ||
        this.sortOption === "queries_asc"
      );
    }
  },
  methods: {
    async listarUsuarios() {
      try {
        const params = {};
        if (this.filterLastDays) params.days = this.filterLastDays;

        const res = await getAPI.get('/api/logs/connected-users-summary/', { params });
        console.log(res.data);
        this.usersOriginal = res.data.filter(user => user.user.toLowerCase() !== 'test');

        this.applyFilters(); // ordenar automáticamente al cargar

      } catch (err) {
        console.error('Error al cargar usuarios:', err);
        this.error = 'Error al cargar usuarios conectados';
      }
    },

    applyFilters() {
      let filtered = [...this.usersOriginal];

      // Filtro por nombre de usuario
      if (this.filterUsername) {
        const search = this.filterUsername.toLowerCase();
        filtered = filtered.filter(user =>
          user.user.toLowerCase().includes(search)
        );
      }

      // Filtro por fecha desde
      if (this.filterFromDate) {
        const from = new Date(this.filterFromDate);
        filtered = filtered.filter(user =>
          new Date(user.last_connected) >= from
        );
      }

      // Filtro por fecha hasta
      if (this.filterToDate) {
        const to = new Date(this.filterToDate);
        to.setHours(23, 59, 59, 999);
        filtered = filtered.filter(user =>
          new Date(user.last_connected) <= to
        );
      }

      if (this.filterMinQueries) {
        filtered = filtered.filter(user =>
          user.queries_count >= this.filterMinQueries
        );
      }

      this.users = filtered;
      this.sortUsers();
    },

    // Método para ordenar usuarios
    sortUsers() {
      if (this.sortOption === "az") {
        this.users.sort((a, b) => a.user.localeCompare(b.user));
      } else if (this.sortOption === "za") {
        this.users.sort((a, b) => b.user.localeCompare(a.user));
      } else if (this.sortOption === "recent") {
        this.users.sort((a, b) => new Date(b.last_connected) - new Date(a.last_connected));
      } else if (this.sortOption === "oldest") {
        this.users.sort((a, b) => new Date(a.last_connected) - new Date(b.last_connected));
      } else if (this.sortOption === "queries_desc") {
        this.users.sort((a, b) => b.queries_count - a.queries_count);
      } else if (this.sortOption === "queries_asc") {
        this.users.sort((a, b) => a.queries_count - b.queries_count);
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Intl.DateTimeFormat('es-ES', {
        dateStyle: 'short',
        timeStyle: 'medium',
        timeZone: 'UTC'   // Evita la conversión automática
      }).format(new Date(dateStr));
    },
    getRanking(index) {
      return index + 1;
    }


  }
}
</script>

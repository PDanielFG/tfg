<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">Usuarios Conectados</h2>

    <div v-if="error" class="mb-4 p-2 bg-red-100 text-red-700 rounded">
      {{ error }}
    </div>

    <!-- Controles de ordenación -->
    <div class="mb-4 flex items-center justify-center gap-4">
      <label class="text-gray-700 font-semibold">Ordenar por:</label>
      <select v-model="sortOption" @change="sortUsers"
        class="px-3 py-2 border rounded-lg bg-white shadow-sm focus:ring focus:ring-blue-300">
        <option value="az">Usuario A → Z</option>
        <option value="za">Usuario Z → A</option>
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
            <th class="w-1/2 px-4 py-3 text-center text-gray-600 font-semibold uppercase">Última Conexión</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <!--Con router link hacemos toda la fila clickable, hacia la nueva vista, eliminamos la etiqeuta tr
          Con el parametro dinámico param, genera un endpoint nuevo usando el ednpoint que acabamos de crear en router index.js
          con name UserProfile/parametro dincamico-->
          <router-link v-for="user in users" :key="user.user" :to="{ name: 'UserProfile', params: { username: user.user } }" class="flex hover:bg-gray-50 cursor-pointer" style="display: table-row;">
            <td class="px-4 py-2 text-gray-700 text-center">{{ user.user }}</td>
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
      error: null,
      sortOption: 'az' // opción por defecto

    }
  },
  created() {
    this.listarUsuarios();
  },
  methods: {
    async listarUsuarios() {
      try {
        const res = await getAPI.get('/api/logs/connected-users/');
        console.log(res.data);
        this.users = res.data.filter(user => user.user.toLowerCase() !== 'test');
        this.sortUsers(); // ordenar automáticamente al cargar

      } catch (err) {
        console.error('Error al cargar usuarios:', err);
        this.error = 'Error al cargar usuarios conectados';
      }
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

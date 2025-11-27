<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">Usuarios Conectados</h2>

    <div v-if="error" class="mb-4 p-2 bg-red-100 text-red-700 rounded">
      {{ error }}
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
          <tr v-for="user in users" :key="user.user" class="hover:bg-gray-50">
            <td class="px-4 py-2 text-gray-700 text-center">{{ user.user }}</td>
            <td class="px-4 py-2 text-gray-700 text-center">{{ formatDate(user.last_connected) }}</td>
          </tr>
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
      error: null
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
        this.users = res.data;
      } catch (err) {
        console.error('Error al cargar usuarios:', err);
        this.error = 'Error al cargar usuarios conectados';
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

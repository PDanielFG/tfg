<template>
  <div>
    <h2>Usuarios conectados</h2>
    <ul>
      <!-- <li v-for="user in users" :key="user.user_host"> -->
      <li v-for="user in users" :key="user.user">      <!--Para mostrar solos los nombres (antes de @), porque en result pusimos user: ----- ya no es user_host que era el nombre del campo de la bd-->
        <!-- {{ user.user_host }} - Última conexión: {{ user.last_connected }} -->
        {{ user.user }} - Última conexión: {{ user.last_connected }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/logs/connected-users/')
    users.value = res.data
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
  }
})
</script>

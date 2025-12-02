<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h1 class="text-2xl font-bold">
      Vista de {{ usuario?.user }}     <!--Aqui llamamos a la propiedad .user, porque asi lo definimos en el diccionario-->
    </h1>
  </div>
</template>


<script>
import { getAPI } from '@/axios-api';

export default {
  name: 'UserProfile',
  data() {
    return {
      usuario: null,   //Esto es lo que podremos usar en el template, por eso va en el return 
      error: null
    };
  },
//   Esto lo hacía para ahorrarnos poner la linea: const username = this.$route.params.username; en created() y 
//   hacer directamente getAPI.get(`/api/users/${this.username}/`)
//   computed: {
//     username() {
//       return this.$route.params.username;
//     }
//   }

  //Se ejecuta cuando se inicia el componente, antes de montarse en el DOOM
  created() {
    //Siguendo la estructura de como siempre lo he hecho
    const username = this.$route.params.username;
    // Traemos los datos del usuario según el username
    getAPI.get(`/api/logs/user/${username}/`)           //Este SII es el endpoint que acabamos de hacer en la API
      .then(response => {
        this.usuario = response.data;
      })
      .catch(err => {
        console.error(err);
        this.error = 'No se pudieron cargar los datos del usuario';
      });
  }
}
</script>

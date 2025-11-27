<template>
  <div>
    <!-- Botón -->
    <button
      @click="openModal"
      class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
      :disabled="loading"
    >
      {{ loading ? "Eliminando..." : "Borrar todos los logs" }}
    </button>

    <!-- Mensaje -->
    <div v-if="message" :class="messageClass" class="mt-2 p-2 rounded text-center">
      {{ message }}
    </div>

    <!-- ===== MODAL ===== -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2 class="text-xl font-semibold mb-4 text-gray-700">
          ¿Eliminar todos los logs?
        </h2>

        <p class="text-gray-600 mb-6">
          Esta acción eliminará todos los registros de manera permanente.  
          ¿Seguro que deseas continuar?
        </p>

        <div class="flex justify-end gap-3">
          <button
            @click="closeModal"
            class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition"
          >
            Cancelar
          </button>

          <button
            @click="deleteAllLogs"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
          >
            Sí, eliminar
          </button>
        </div>
      </div>
    </div>
    <!-- ================= -->
  </div>
</template>

<script>
import { getAPI } from '@/axios-api';

export default {
  name: "DeleteButton",
  data() {
    return {
      loading: false,
      message: null,
      success: false,
      showModal: false,  // control del modal
    };
  },
  computed: {
    messageClass() {
      return this.success ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700";
    },
  },
  methods: {
    openModal() {
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },

    async deleteAllLogs() {
      this.loading = true;

      try {
        const res = await getAPI.delete("/api/logs/delete_all/");
        this.success = true;
        this.message = `Logs eliminados correctamente: ${res.data.deleted_records}`;
        this.$emit("deleted");
      } catch (err) {
        console.error(err);
        this.success = false;
        this.message = "Error al eliminar los logs";
      } finally {
        this.loading = false;
        this.closeModal();
      }
    },
  },
};
</script>

<style scoped>
/* Fondo oscuro del modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* Caja blanca del modal */
.modal-content {
  background: white;
  padding: 25px;
  width: 400px;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}
</style>

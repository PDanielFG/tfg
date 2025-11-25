<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 p-6">
    <div
      class="w-full max-w-lg bg-white shadow-xl rounded-2xl p-8 border border-gray-200"
    >
      <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
        Subir archivo .log
      </h2>

      <!-- File input -->
      <label
        class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition"
      >
        <div class="flex flex-col items-center">
          <svg
            class="w-10 h-10 text-gray-400 mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16V4m0 0L3 8m4-4l4 4m6 12V12m0 0l4 4m-4-4l-4 4"
            />
          </svg>

          <span class="text-gray-500 text-sm">
            {{ selectedFile ? selectedFile.name : "Selecciona un archivo .log" }}
          </span>
        </div>

        <input
          type="file"
          accept=".log"
          @change="onFileChange"
          class="hidden"
        />
      </label>

      <!-- Upload button -->
      <button
        @click="uploadFile"
        :disabled="!selectedFile"
        class="mt-6 w-full py-3 rounded-xl font-semibold transition
          bg-blue-600 text-white hover:bg-blue-700
          disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Subir archivo
      </button>

      <!-- Response -->
      <div
        v-if="response"
        class="mt-6 bg-gray-50 rounded-xl p-4 border border-gray-200"
      >
        <h3 class="font-semibold text-gray-700 mb-2">
          Respuesta del servidor:
        </h3>
        <pre class="text-sm text-gray-800 whitespace-pre-wrap">
{{ response }}
        </pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const selectedFile = ref(null);
const response = ref(null);

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

const uploadFile = async () => {
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const res = await axios.post("http://localhost:8000/api/logs/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    response.value = res.data;
  } catch (error) {
    console.error(error);
    response.value = error.response?.data || "Error al subir archivo";
  }
};
</script>

<style scoped>
</style>

<template>
  <div class="upload-container">
    <h2>Subir archivo .log</h2>

    <input type="file" accept=".log" @change="onFileChange" />

    <button @click="uploadFile" :disabled="!selectedFile">
      Subir archivo
    </button>

    <div v-if="response">
      <h3>Respuesta del servidor:</h3>
      <pre>{{ response }}</pre>
    </div>

  </div>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"

const selectedFile = ref(null)
const response = ref(null)

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

const uploadFile = async () => {
  const formData = new FormData()
  formData.append("file", selectedFile.value)

  try {
    const res = await axios.post("http://localhost:8000/api/logs/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    response.value = res.data
  } catch (error) {
    console.error(error)
    response.value = error.response?.data || "Error al subir archivo"
  }
}
</script>

<style>
.upload-container {
  padding: 20px;
}
</style>

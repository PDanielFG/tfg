<template>
    <div class="p-6 bg-gray-100 min-h-screen">

        <h2 class="text-xl font-semibold text-gray-700 mb-3 text-center">
            Resumen datos de grupo
        </h2>

        <h1 class="text-l font-bold mb-3">
            <router-link
                class="inline-block px-6 py-2 text-white font-semibold rounded-lg shadow-md transition-all duration-200 bg-[#42b983] hover:bg-[#369870] active:scale-95 cursor-pointer"
                :to="{ name: 'GroupGeneral' }">Volver a gráficos</router-link>
        </h1>
    </div>

</template>
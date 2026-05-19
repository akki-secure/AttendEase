export default defineNuxtConfig({
  devtools: { enabled: false },

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vee-validate/nuxt"],

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? "http://localhost:8000",
    },
  },

  nitro: {
    devProxy: {
      "/api": {
        target: process.env.NUXT_PUBLIC_API_BASE ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },

  typescript: {
    strict: true,
  },

  compatibilityDate: "2024-11-01",
})

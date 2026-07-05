export default defineNuxtConfig({
  devtools: { enabled: false },

  // EC2ではAWSのhairpin NAT制限（インスタンスが自身のパブリックIPに到達できない）により
  // SSRがハングするため、NUXT_SSR=false で明示的にSPAモードに切り替える（PR #11参照）。
  // ローカル/Docker Compose開発では既定でSSRを有効にする。
  ssr: process.env.NUXT_SSR !== "false",

  modules: ["@nuxt/ui", "@pinia/nuxt", "@vee-validate/nuxt"],

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    // SSR（サーバー側fetch）専用。Docker Compose環境ではフロントエンドコンテナから
    // "localhost:8000" は自分自身を指してしまいbackendに届かないため、コンテナ間通信可能な
    // ホスト名（例: http://backend:8000）を指定する。未設定時はpublic.apiBaseにフォールバック。
    apiBaseServer: process.env.NUXT_API_BASE_SERVER ?? process.env.NUXT_PUBLIC_API_BASE ?? "http://localhost:8000",
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

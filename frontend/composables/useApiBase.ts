// SSR実行時（Docker Composeのフロントエンドコンテナ内）とブラウザ実行時とで
// backendへの到達可能なURLが異なるため、実行環境に応じて出し分ける。
export function useApiBase(): string {
  const config = useRuntimeConfig()
  return import.meta.server ? config.apiBaseServer : config.public.apiBase
}

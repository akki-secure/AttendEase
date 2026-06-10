import { onUnmounted } from "vue"
import { useForm } from "vee-validate"
import { toTypedSchema } from "@vee-validate/zod"
import { z } from "zod"
import { ASCII_ONLY, extractApiError } from "~/utils/validation"

const requestSchema = toTypedSchema(
  z.object({
    employee_id: z.string().min(1, "社員IDを入力してください"),
  })
)

const confirmSchema = toTypedSchema(
  z.object({
    token: z
      .string()
      .length(6, "6桁の数字を入力してください")
      .regex(/^\d{6}$/, "半角数字6桁を入力してください"),
    new_password: z
      .string()
      .min(1, "新しいパスワードを入力してください")
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(ASCII_ONLY, "パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）"),
    confirm_password: z.string().min(1, "確認用パスワードを入力してください"),
  }).refine((v) => v.new_password === v.confirm_password, {
    message: "パスワードが一致しません",
    path: ["confirm_password"],
  })
)

export function usePasswordResetForm() {
  const config = useRuntimeConfig()
  const step = ref<"request" | "confirm" | "done">("request")
  const storedEmployeeId = ref("")
  const emailHint = ref("")
  const apiError = ref<string | null>(null)

  const resendCooldown = ref(0)
  const isResending = ref(false)
  let cooldownTimer: ReturnType<typeof setInterval> | null = null

  function startCooldown() {
    resendCooldown.value = 60
    if (cooldownTimer) clearInterval(cooldownTimer)
    cooldownTimer = setInterval(() => {
      resendCooldown.value--
      if (resendCooldown.value <= 0) {
        clearInterval(cooldownTimer!)
        cooldownTimer = null
      }
    }, 1000)
  }

  const requestForm = useForm({ validationSchema: requestSchema, validateOnMount: false })
  const [employeeId, employeeIdAttrs] = requestForm.defineField("employee_id", { validateOnModelUpdate: true })

  const confirmForm = useForm({ validationSchema: confirmSchema, validateOnMount: false })
  const [token, tokenAttrs] = confirmForm.defineField("token", { validateOnModelUpdate: true })
  const [newPassword, newPasswordAttrs] = confirmForm.defineField("new_password", { validateOnModelUpdate: true })
  const [confirmPassword, confirmPasswordAttrs] = confirmForm.defineField("confirm_password", { validateOnModelUpdate: true })

  const onSubmitRequest = requestForm.handleSubmit(async (values) => {
    apiError.value = null
    try {
      const data = await $fetch<{ ok: boolean; email_hint: string }>(
        `${config.public.apiBase}/api/v1/auth/password-reset/request`,
        { method: "POST", body: { employee_id: values.employee_id } }
      )
      storedEmployeeId.value = values.employee_id
      emailHint.value = data.email_hint
      step.value = "confirm"
      startCooldown()
    } catch (err: unknown) {
      apiError.value = extractApiError(err, "送信に失敗しました。もう一度お試しください。")
      throw err
    }
  })

  const onSubmitConfirm = confirmForm.handleSubmit(async (values) => {
    apiError.value = null
    try {
      await $fetch(`${config.public.apiBase}/api/v1/auth/password-reset/confirm`, {
        method: "POST",
        body: {
          employee_id: storedEmployeeId.value,
          token: values.token,
          new_password: values.new_password,
        },
      })
      step.value = "done"
    } catch (err: unknown) {
      apiError.value = extractApiError(err, "パスワードのリセットに失敗しました。もう一度お試しください。")
      throw err
    }
  })

  async function resendToken() {
    if (resendCooldown.value > 0 || isResending.value) return
    isResending.value = true
    apiError.value = null
    try {
      const data = await $fetch<{ ok: boolean; email_hint: string }>(
        `${config.public.apiBase}/api/v1/auth/password-reset/request`,
        { method: "POST", body: { employee_id: storedEmployeeId.value } }
      )
      emailHint.value = data.email_hint
      confirmForm.resetForm()
      startCooldown()
    } catch (err: unknown) {
      apiError.value = extractApiError(err, "再送信に失敗しました。")
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 429) startCooldown()
    } finally {
      isResending.value = false
    }
  }

  onUnmounted(() => {
    if (cooldownTimer) clearInterval(cooldownTimer)
  })

  function backToRequest() {
    step.value = "request"
    storedEmployeeId.value = ""
    emailHint.value = ""
    apiError.value = null
    if (cooldownTimer) clearInterval(cooldownTimer)
    resendCooldown.value = 0
  }

  return {
    step,
    employeeId, employeeIdAttrs,
    token, tokenAttrs,
    newPassword, newPasswordAttrs,
    confirmPassword, confirmPasswordAttrs,
    emailHint,
    apiError,
    resendCooldown,
    isResending,
    requestErrors: requestForm.errors,
    confirmErrors: confirmForm.errors,
    isSubmittingRequest: requestForm.isSubmitting,
    isSubmittingConfirm: confirmForm.isSubmitting,
    onSubmitRequest,
    onSubmitConfirm,
    resendToken,
    backToRequest,
  }
}

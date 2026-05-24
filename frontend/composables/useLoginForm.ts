import { useForm } from "vee-validate"
import { toTypedSchema } from "@vee-validate/zod"
import { z } from "zod"
import { useAuthStore } from "~/stores/auth"
import { ASCII_ONLY } from "~/utils/validation"

const credentialsSchema = toTypedSchema(
  z.object({
    employee_id: z.string().min(1, "社員IDを入力してください"),
    password: z
      .string()
      .min(1, "パスワードを入力してください")
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(ASCII_ONLY, "パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）"),
  })
)

const otpSchema = toTypedSchema(
  z.object({
    otp: z
      .string()
      .length(6, "6桁の数字を入力してください")
      .regex(/^\d{6}$/, "半角数字6桁を入力してください"),
  })
)

export function useLoginForm() {
  const authStore = useAuthStore()
  const step = ref<"credentials" | "otp">("credentials")
  const storedEmployeeId = ref("")
  const emailHint = ref("")

  // 再送信クールダウン
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

  // ステップ1: 社員ID + パスワード
  const credentialsForm = useForm({ validationSchema: credentialsSchema, validateOnMount: false })
  const [employeeId, employeeIdAttrs] = credentialsForm.defineField("employee_id", { validateOnModelUpdate: true })
  const [password, passwordAttrs] = credentialsForm.defineField("password", { validateOnModelUpdate: true })

  // ステップ2: OTP
  const otpForm = useForm({ validationSchema: otpSchema, validateOnMount: false })
  const [otp, otpAttrs] = otpForm.defineField("otp", { validateOnModelUpdate: true })

  const onSubmitCredentials = credentialsForm.handleSubmit(async (values) => {
    const res = await authStore.preCheck({ employee_id: values.employee_id, password: values.password })
    storedEmployeeId.value = values.employee_id
    emailHint.value = res.email_hint
    step.value = "otp"
    startCooldown()
  })

  const onSubmitOtp = otpForm.handleSubmit(async (values) => {
    await authStore.login({
      employee_id: storedEmployeeId.value,
      otp: values.otp,
    })
    storedEmployeeId.value = ""
  })

  async function resendOtp() {
    if (resendCooldown.value > 0 || isResending.value) return
    isResending.value = true
    authStore.clearError()
    try {
      const storedPassword = credentialsForm.values.password ?? ""
      const res = await authStore.preCheck({
        employee_id: storedEmployeeId.value,
        password: storedPassword,
      })
      emailHint.value = res.email_hint
      otpForm.resetForm()
      startCooldown()
    } finally {
      isResending.value = false
    }
  }

  function backToCredentials() {
    step.value = "credentials"
    storedEmployeeId.value = ""
    emailHint.value = ""
    if (cooldownTimer) clearInterval(cooldownTimer)
    resendCooldown.value = 0
    authStore.clearError()
  }

  return {
    step,
    employeeId,
    employeeIdAttrs,
    password,
    passwordAttrs,
    otp,
    otpAttrs,
    emailHint,
    resendCooldown,
    isResending,
    credentialsErrors: credentialsForm.errors,
    otpErrors: otpForm.errors,
    isSubmittingCredentials: credentialsForm.isSubmitting,
    isSubmittingOtp: otpForm.isSubmitting,
    onSubmitCredentials,
    onSubmitOtp,
    resendOtp,
    backToCredentials,
    authStore,
  }
}

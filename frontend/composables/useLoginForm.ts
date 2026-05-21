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

const passphraseSchema = toTypedSchema(
  z.object({
    passphrase: z.string().min(1, "合言葉を入力してください"),
  })
)

export function useLoginForm() {
  const authStore = useAuthStore()
  const step = ref<"credentials" | "passphrase">("credentials")
  const storedCredentials = ref({ employee_id: "", password: "" })

  // ステップ1: 社員ID + パスワード
  const credentialsForm = useForm({ validationSchema: credentialsSchema, validateOnMount: false })
  const [employeeId, employeeIdAttrs] = credentialsForm.defineField("employee_id", { validateOnModelUpdate: true })
  const [password, passwordAttrs] = credentialsForm.defineField("password", { validateOnModelUpdate: true })

  // ステップ2: 合言葉
  const passphraseForm = useForm({ validationSchema: passphraseSchema, validateOnMount: false })
  const [passphrase, passphraseAttrs] = passphraseForm.defineField("passphrase", { validateOnModelUpdate: true })

  const onSubmitCredentials = credentialsForm.handleSubmit(async (values) => {
    await authStore.preCheck({ employee_id: values.employee_id, password: values.password })
    storedCredentials.value = { employee_id: values.employee_id, password: values.password }
    step.value = "passphrase"
  })

  const onSubmitPassphrase = passphraseForm.handleSubmit(async (values) => {
    try {
      await authStore.login({
        employee_id: storedCredentials.value.employee_id,
        password: storedCredentials.value.password,
        passphrase: values.passphrase,
      })
    } finally {
      storedCredentials.value = { employee_id: "", password: "" }
    }
  })

  function backToCredentials() {
    step.value = "credentials"
    storedCredentials.value = { employee_id: "", password: "" }
    authStore.clearError()
  }

  return {
    step,
    employeeId,
    employeeIdAttrs,
    password,
    passwordAttrs,
    passphrase,
    passphraseAttrs,
    credentialsErrors: credentialsForm.errors,
    passphraseErrors: passphraseForm.errors,
    isSubmittingCredentials: credentialsForm.isSubmitting,
    isSubmittingPassphrase: passphraseForm.isSubmitting,
    onSubmitCredentials,
    onSubmitPassphrase,
    backToCredentials,
    authStore,
  }
}

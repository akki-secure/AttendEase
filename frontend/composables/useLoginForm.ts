import { useForm } from "vee-validate"
import { toTypedSchema } from "@vee-validate/zod"
import { z } from "zod"
import { useAuthStore } from "~/stores/auth"

const ASCII_ONLY = /^[\x20-\x7E]+$/

const loginSchema = toTypedSchema(
  z.object({
    employee_id: z.string().min(1, "社員IDを入力してください"),
    password: z
      .string()
      .min(1, "パスワードを入力してください")
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(ASCII_ONLY, "パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）"),
  })
)

export function useLoginForm() {
  const authStore = useAuthStore()

  const { handleSubmit, defineField, errors, isSubmitting } = useForm({
    validationSchema: loginSchema,
    validateOnMount: false,
  })

  const [employeeId, employeeIdAttrs] = defineField("employee_id", {
    validateOnModelUpdate: true,
  })

  const [password, passwordAttrs] = defineField("password", {
    validateOnModelUpdate: true,
  })

  const onSubmit = handleSubmit(async (values) => {
    await authStore.login({ employee_id: values.employee_id, password: values.password })
  })

  return {
    employeeId,
    employeeIdAttrs,
    password,
    passwordAttrs,
    errors,
    isSubmitting,
    onSubmit,
    authStore,
  }
}

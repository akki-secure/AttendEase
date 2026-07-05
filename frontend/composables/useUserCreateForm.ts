import { useForm } from "vee-validate"
import { toTypedSchema } from "@vee-validate/zod"
import { z } from "zod"
import type { UserCreateRequest, UserResponse } from "~/types/auth"
import { ASCII_ONLY } from "~/utils/validation"

const userCreateSchema = toTypedSchema(
  z.object({
    name: z.string().min(1, "ユーザー名を入力してください"),
    employee_id: z.string().min(1, "社員IDを入力してください"),
    password: z
      .string()
      .min(1, "パスワードを入力してください")
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(ASCII_ONLY, "パスワードに使用できない文字が含まれています（日本語・全角文字は使用不可）"),
    role: z.enum(["EMPLOYEE", "MANAGER", "ADMIN"]),
  })
)

export function useUserCreateForm() {
  const apiBase = useApiBase()
  const authStore = useAuthStore()

  const apiError = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

  const { handleSubmit, defineField, errors, isSubmitting, resetForm } = useForm({
    validationSchema: userCreateSchema,
    initialValues: { role: "EMPLOYEE" as const },
    validateOnMount: false,
  })

  const [name, nameAttrs] = defineField("name", { validateOnModelUpdate: true })
  const [employeeId, employeeIdAttrs] = defineField("employee_id", { validateOnModelUpdate: true })
  const [password, passwordAttrs] = defineField("password", { validateOnModelUpdate: true })
  const [role, roleAttrs] = defineField("role", { validateOnModelUpdate: false })

  const onSubmit = handleSubmit(async (values) => {
    apiError.value = null
    successMessage.value = null

    try {
      const data = await $fetch<UserResponse>(`${apiBase}/api/v1/admin/users`, {
        method: "POST",
        headers: { Authorization: `Bearer ${authStore.token}` },
        body: values as UserCreateRequest,
      })
      successMessage.value = `${data.name}（${data.employee_id}）を登録しました`
      resetForm()
    } catch (err: unknown) {
      const fetchError = err as { data?: { detail?: string } }
      apiError.value = fetchError?.data?.detail ?? "登録に失敗しました。もう一度お試しください。"
    }
  })

  return {
    name, nameAttrs,
    employeeId, employeeIdAttrs,
    password, passwordAttrs,
    role, roleAttrs,
    errors,
    isSubmitting,
    apiError,
    successMessage,
    onSubmit,
  }
}

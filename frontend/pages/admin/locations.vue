<script setup lang="ts">
import type { GeofenceSetting, OfficeLocation } from "~/types/location"

definePageMeta({ middleware: "admin" })

const apiBase = useApiBase()
const authHeaders = useAuthHeaders()
const toast = useToast()

const locations = ref<OfficeLocation[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const setting = ref<GeofenceSetting>({ enabled: false })
const settingSaving = ref(false)

async function fetchLocations() {
  isLoading.value = true
  error.value = null
  try {
    locations.value = await $fetch<OfficeLocation[]>(
      `${apiBase}/api/v1/admin/locations`,
      { headers: authHeaders() },
    )
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    error.value = e?.data?.detail ?? "拠点の取得に失敗しました"
  } finally {
    isLoading.value = false
  }
}

async function fetchSetting() {
  try {
    setting.value = await $fetch<GeofenceSetting>(
      `${apiBase}/api/v1/admin/geofence-settings`,
      { headers: authHeaders() },
    )
  } catch { /* non-critical */ }
}

await Promise.all([fetchLocations(), fetchSetting()])

async function toggleGeofence(enabled: boolean) {
  settingSaving.value = true
  try {
    setting.value = await $fetch<GeofenceSetting>(
      `${apiBase}/api/v1/admin/geofence-settings`,
      { method: "PUT", headers: authHeaders(), body: { enabled } },
    )
    toast.add({
      title: enabled ? "ジオフェンス制限をONにしました" : "ジオフェンス制限をOFFにしました",
      color: enabled ? "green" : "gray",
      icon: "i-heroicons-check-circle",
    })
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    toast.add({ title: e?.data?.detail ?? "設定の更新に失敗しました", color: "red", icon: "i-heroicons-exclamation-circle" })
    setting.value = { ...setting.value } // revert表示のためのトリガー
    await fetchSetting()
  } finally {
    settingSaving.value = false
  }
}

// ─── 拠点 登録・編集モーダル ───────────────────────────
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const formName = ref("")
const formLat = ref<number | null>(null)
const formLon = ref<number | null>(null)
const formRadius = ref(200)
const formActive = ref(true)
const modalError = ref<string | null>(null)
const modalLoading = ref(false)
const locatingCurrentPos = ref(false)

function openCreateModal() {
  editingId.value = null
  formName.value = ""
  formLat.value = null
  formLon.value = null
  formRadius.value = 200
  formActive.value = true
  modalError.value = null
  modalOpen.value = true
}

function openEditModal(loc: OfficeLocation) {
  editingId.value = loc.id
  formName.value = loc.name
  formLat.value = loc.latitude
  formLon.value = loc.longitude
  formRadius.value = loc.radius_meters
  formActive.value = loc.is_active
  modalError.value = null
  modalOpen.value = true
}

function useCurrentPosition() {
  if (!navigator.geolocation) {
    modalError.value = "この端末では位置情報を取得できません"
    return
  }
  locatingCurrentPos.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      formLat.value = Math.round(pos.coords.latitude * 1e6) / 1e6
      formLon.value = Math.round(pos.coords.longitude * 1e6) / 1e6
      locatingCurrentPos.value = false
    },
    () => {
      modalError.value = "現在地の取得に失敗しました。位置情報の利用を許可してください"
      locatingCurrentPos.value = false
    },
    { enableHighAccuracy: true, timeout: 8000 },
  )
}

async function submitLocation() {
  modalError.value = null
  if (!formName.value.trim()) {
    modalError.value = "拠点名を入力してください"
    return
  }
  if (formLat.value == null || formLon.value == null) {
    modalError.value = "緯度・経度を入力してください"
    return
  }
  modalLoading.value = true
  try {
    const body = {
      name: formName.value.trim(),
      latitude: formLat.value,
      longitude: formLon.value,
      radius_meters: formRadius.value,
      is_active: formActive.value,
    }
    if (editingId.value != null) {
      await $fetch(`${apiBase}/api/v1/admin/locations/${editingId.value}`, {
        method: "PUT", headers: authHeaders(), body,
      })
    } else {
      await $fetch(`${apiBase}/api/v1/admin/locations`, {
        method: "POST", headers: authHeaders(), body,
      })
    }
    modalOpen.value = false
    await fetchLocations()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    modalError.value = e?.data?.detail ?? "保存に失敗しました"
  } finally {
    modalLoading.value = false
  }
}

async function deleteLocation(loc: OfficeLocation) {
  if (!confirm(`「${loc.name}」を削除しますか？`)) return
  try {
    await $fetch(`${apiBase}/api/v1/admin/locations/${loc.id}`, {
      method: "DELETE", headers: authHeaders(),
    })
    await fetchLocations()
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    toast.add({ title: e?.data?.detail ?? "削除に失敗しました", color: "red", icon: "i-heroicons-exclamation-circle" })
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-clock" class="w-7 h-7 text-primary-600" />
        <span class="text-lg font-bold text-gray-800">AttendEase</span>
        <UBadge color="orange" variant="soft" class="ml-1">管理者</UBadge>
      </div>
      <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-left" to="/">
        ダッシュボードへ戻る
      </UButton>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-10 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <UIcon name="i-heroicons-map-pin" class="w-7 h-7 text-primary-600" />
            拠点・ジオフェンス管理
          </h1>
          <p class="mt-1 text-sm text-gray-500">出退勤打刻を許可する拠点の位置情報を管理します。</p>
        </div>
        <UButton color="primary" icon="i-heroicons-plus" @click="openCreateModal">拠点を追加</UButton>
      </div>

      <!-- ジオフェンス ON/OFF -->
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="font-semibold text-gray-800">ジオフェンス制限</p>
            <p class="text-sm text-gray-500 mt-0.5">
              ONにすると、登録された拠点の範囲外からは出退勤打刻ができなくなります。
              拠点が1件も登録されていない場合はONでも制限されません。
            </p>
          </div>
          <UToggle
            :model-value="setting.enabled"
            :loading="settingSaving"
            :disabled="settingSaving"
            @update:model-value="toggleGeofence"
          />
        </div>
      </UCard>

      <UAlert
        v-if="error"
        color="red"
        variant="soft"
        icon="i-heroicons-exclamation-circle"
        :description="error"
      />

      <UCard>
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="locations.length === 0" class="flex flex-col items-center justify-center py-12 gap-2">
          <UIcon name="i-heroicons-map-pin" class="w-8 h-8 text-gray-300" />
          <p class="text-gray-400 text-sm">拠点が登録されていません</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">拠点名</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">緯度・経度</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">許容半径</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">状態</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="loc in locations" :key="loc.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3 font-medium text-gray-700">{{ loc.name }}</td>
                <td class="px-4 py-3 font-mono text-gray-500 text-xs">{{ loc.latitude }}, {{ loc.longitude }}</td>
                <td class="px-4 py-3 text-right text-gray-600">{{ loc.radius_meters }}m</td>
                <td class="px-4 py-3">
                  <UBadge :color="loc.is_active ? 'green' : 'gray'" variant="subtle" size="xs">
                    {{ loc.is_active ? '有効' : '無効' }}
                  </UBadge>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <UButton color="gray" variant="ghost" size="xs" icon="i-heroicons-pencil" @click="openEditModal(loc)">編集</UButton>
                    <UButton color="red" variant="ghost" size="xs" icon="i-heroicons-trash" @click="deleteLocation(loc)">削除</UButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>
    </main>

    <!-- 拠点 登録・編集モーダル -->
    <UModal v-model="modalOpen">
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-map-pin" class="w-5 h-5 text-primary-500" />
            <span class="font-semibold text-gray-800">{{ editingId != null ? '拠点を編集' : '拠点を追加' }}</span>
          </div>
        </template>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">拠点名</label>
            <input
              v-model="formName"
              type="text"
              placeholder="例: 本社オフィス"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            >
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">緯度</label>
              <input
                v-model.number="formLat"
                type="number"
                step="0.000001"
                placeholder="35.681236"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-400"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">経度</label>
              <input
                v-model.number="formLon"
                type="number"
                step="0.000001"
                placeholder="139.767125"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-400"
              >
            </div>
          </div>

          <UButton
            color="gray" variant="soft" size="xs" icon="i-heroicons-cursor-arrow-rays"
            :loading="locatingCurrentPos" :disabled="locatingCurrentPos"
            @click="useCurrentPosition"
          >現在地を使用</UButton>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">許容半径（メートル）</label>
            <input
              v-model.number="formRadius"
              type="number"
              min="10"
              max="5000"
              step="10"
              class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
            >
          </div>

          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700">有効にする</label>
            <UToggle v-model="formActive" />
          </div>

          <div v-if="modalError" class="flex items-center gap-2 text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">
            <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 flex-shrink-0" />
            {{ modalError }}
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="outline" @click="modalOpen = false">キャンセル</UButton>
            <UButton
              color="primary"
              :loading="modalLoading"
              icon="i-heroicons-check"
              @click="submitLocation"
            >保存</UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

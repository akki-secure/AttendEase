<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue?: string | null
  inputClass?: string
  disabled?: boolean
  placeholder?: string
}>(), {
  modelValue: null,
  inputClass: '',
  disabled: false,
  placeholder: '--:--',
})

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const open = ref(false)
const rootEl = ref<HTMLElement | null>(null)
const hourListEl = ref<HTMLElement | null>(null)
const minuteListEl = ref<HTMLElement | null>(null)

const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))
const minutes = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0'))

const hourVal = computed(() => props.modelValue?.split(':')[0] ?? null)
const minuteVal = computed(() => props.modelValue?.split(':')[1] ?? null)

function scrollSelectedIntoView() {
  nextTick(() => {
    hourListEl.value?.querySelector('[data-selected="true"]')?.scrollIntoView({ block: 'center' })
    minuteListEl.value?.querySelector('[data-selected="true"]')?.scrollIntoView({ block: 'center' })
  })
}

function toggle() {
  if (props.disabled) return
  open.value = !open.value
  if (open.value) scrollSelectedIntoView()
}

function selectHour(h: string) {
  emit('update:modelValue', `${h}:${minuteVal.value ?? '00'}`)
}

function selectMinute(m: string) {
  emit('update:modelValue', `${hourVal.value ?? '00'}:${m}`)
  open.value = false
}

function onClickOutside(e: MouseEvent) {
  if (open.value && rootEl.value && !rootEl.value.contains(e.target as Node)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<template>
  <div ref="rootEl" class="relative inline-block w-full">
    <button
      type="button"
      :disabled="disabled"
      :class="[inputClass, 'flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed']"
      @click="toggle"
    >
      <span>{{ modelValue || placeholder }}</span>
      <UIcon name="i-heroicons-clock" class="w-[0.85em] h-[0.85em] opacity-60 shrink-0" />
    </button>

    <div
      v-if="open"
      class="absolute left-0 top-full mt-1 z-50 flex bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden"
    >
      <div ref="hourListEl" class="w-16 max-h-56 overflow-y-auto py-1">
        <button
          v-for="h in hours" :key="h" type="button"
          :data-selected="h === hourVal"
          class="w-full text-center py-2 text-sm font-mono hover:bg-gray-100"
          :class="h === hourVal ? 'bg-brand-600 text-white font-bold hover:bg-brand-600' : 'text-gray-700'"
          @click="selectHour(h)"
        >{{ h }}</button>
      </div>
      <div ref="minuteListEl" class="w-16 max-h-56 overflow-y-auto py-1 border-l border-gray-100">
        <button
          v-for="m in minutes" :key="m" type="button"
          :data-selected="m === minuteVal"
          class="w-full text-center py-2 text-sm font-mono hover:bg-gray-100"
          :class="m === minuteVal ? 'bg-brand-600 text-white font-bold hover:bg-brand-600' : 'text-gray-700'"
          @click="selectMinute(m)"
        >{{ m }}</button>
      </div>
    </div>
  </div>
</template>

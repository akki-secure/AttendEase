<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4 shadow-lg">
          <UIcon name="i-heroicons-clock" class="w-9 h-9 text-white" />
        </div>
        <h1 class="text-3xl font-bold text-gray-900">AttendEase</h1>
        <p class="mt-1 text-sm text-gray-500">勤怠管理システム</p>
      </div>

      <UCard class="shadow-xl">
        <slot />
      </UCard>

      <p class="text-center text-xs text-gray-400 mt-6">
        © {{ new Date().getFullYear() }} AttendEase. All rights reserved.
      </p>
    </div>
  </div>
</template>

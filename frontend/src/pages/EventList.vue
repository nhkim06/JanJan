<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-start pt-12 px-6 font-sans relative"
  >
    <div class="w-full max-w-md md:max-w-2xl lg:max-w-4xl flex items-center mb-6">
      <button
        @click="router.back()"
        class="mr-4 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
      >
        <font-awesome-icon icon="fa-solid fa-chevron-left" />
      </button>
      <h1 class="text-2xl md:text-3xl font-black text-slate-900 truncate">{{ pageTitle }}</h1>
    </div>

    <div class="w-full max-w-md md:max-w-2xl lg:max-w-4xl mb-8 text-left">
      <p class="text-sm md:text-base text-slate-400 font-bold ml-1">{{ pageDescription }}</p>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 w-full max-w-md md:max-w-2xl lg:max-w-4xl">
      <button
        v-for="(item, index) in options"
        :key="index"
        @click="selectOption(item.key)"
        class="bg-white border border-slate-100 rounded-3xl p-6 flex flex-col items-center justify-center aspect-square shadow-[0_8px_30px_rgb(0,0,0,0.012)] hover:shadow-md hover:border-indigo-100 transition-all duration-200 group active:scale-[0.98]"
      >
        <div
          class="w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-indigo-50/70 flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors duration-200"
        >
          <font-awesome-icon :icon="item.icon" class="text-xl md:text-2xl text-indigo-600" />
        </div>

        <span class="text-base md:text-lg font-bold text-slate-800 text-center">{{ item.title }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import eventsData from '../assets/events.json';

const route = useRoute();
const router = useRouter();
const category = computed(() => route.params.category as string);

const eventInfo = computed(() => {
  return (eventsData as any)[category.value] || {
    title: 'Select Event',
    description: 'Please select an event',
    options: []
  };
});

const pageTitle = computed(() => eventInfo.value.title);
const pageDescription = computed(() => eventInfo.value.description);
const options = computed(() => eventInfo.value.options);

const selectOption = (key: string) => {
  if (key) {
    router.push(`/forms/${key}`);
  }
};
</script>

<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-start pt-16 px-6 font-sans"
  >
    <div class="w-full max-w-md mb-8 text-left">
      <h1 class="text-2xl font-bold text-slate-900 mb-2">상세 상황 선택</h1>
      <p class="text-sm text-slate-400 font-medium">축하할 일을 선택해주세요</p>
    </div>

    <div class="grid grid-cols-2 gap-4 w-full max-w-md">
      <button
        v-for="(item, index) in options"
        :key="index"
        @click="selectOption(item.title)"
        class="bg-white border border-slate-100 rounded-3xl p-6 flex flex-col items-center justify-center aspect-square shadow-[0_8px_30px_rgb(0,0,0,0.012)] hover:shadow-md hover:border-indigo-100 transition-all duration-200 group active:scale-[0.98]"
      >
        <div
          class="w-16 h-16 rounded-2xl bg-indigo-50/70 flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors duration-200"
        >
          <i :class="[item.icon, 'text-xl text-indigo-600']"></i>
        </div>

        <span class="text-base font-bold text-slate-800">{{ item.title }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 카드 데이터 배열
const options = ref([
  { title: '결혼식', icon: 'fa-regular fa-heart' },
  { title: '승진/취업', icon: 'fa-solid fa-arrow-trend-up' },
  { title: '출산', icon: 'fa-solid fa-baby' },
  { title: '입학/졸업', icon: 'fa-solid fa-graduation-cap' },
  { title: '퇴직/이직', icon: 'fa-solid fa-right-from-bracket' },
]);

// 클릭 이벤트 핸들러
const selectOption = (title) => {
  console.log(`${title} 선택됨`);
  // 부모 컴포넌트로 emit 하거나 라우터 이동 로직을 여기에 작성하세요.
};
</script>

<style scoped>
/* 추가적인 커스텀 스타일이 필요하다면 여기에 작성 (Tailwind로 대부분 해결 가능) */
</style>

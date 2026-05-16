<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-start p-6 font-sans text-slate-800"
  >
    <div class="w-full max-w-md space-y-6 relative">
      <!-- 상단 네비게이션 -->
      <div class="flex items-center justify-between w-full py-2">
        <button
          @click="goHome"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200/70 shadow-sm text-slate-600 hover:bg-slate-50 active:scale-95 transition"
          title="처음으로 이동"
        >
          <font-awesome-icon icon="fa-solid fa-house" class="h-5 w-5" />
        </button>
        <span class="text-sm font-semibold text-slate-500">진단 결과</span>
        <div class="w-10"></div>
      </div>

      <!-- 요약 정보 -->
      <div
        class="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 mb-2"
      >
        <div class="flex items-center justify-between mb-4">
          <span
            class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-xs font-bold"
          >
            {{ categoryName }}
          </span>
          <span class="text-xs font-bold text-slate-400">
            기준: {{ cultureBase }}
          </span>
        </div>
        <h1 class="text-xl font-bold text-slate-900 leading-tight">
          <span class="text-indigo-600">{{ targetName }}</span
          >님을 위한<br />
          맞춤 가이드가 도착했습니다.
        </h1>
      </div>

      <!-- 금액 추천 섹션 -->
      <div
        class="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 text-center relative overflow-hidden"
      >
        <h2 class="text-sm font-medium text-slate-400 mb-2">적정 추천 금액</h2>
        <div class="text-5xl font-black tracking-tight mb-2 text-slate-900">
          50,000<span class="text-2xl font-bold text-indigo-600 ml-1">원</span>
        </div>
        <p class="text-sm font-semibold text-slate-400 mb-6">
          최소 30,000원 이상
        </p>

        <div
          class="bg-emerald-50/50 rounded-2xl p-4 flex items-center justify-start border border-emerald-100/50"
        >
          <span class="text-emerald-500 mr-2 flex items-center">
            <font-awesome-icon
              icon="fa-solid fa-circle-check"
              class="h-5 w-5"
            />
          </span>
          <p class="text-sm font-medium text-slate-600">
            안 가고 3만원 or 가고 5만원
          </p>
        </div>
      </div>

      <!-- 금기사항 -->
      <div class="bg-rose-50/40 rounded-3xl p-6 border border-rose-100/70">
        <div class="flex items-center text-rose-600 font-bold mb-4">
          <font-awesome-icon
            icon="fa-solid fa-triangle-exclamation"
            class="h-5 w-5 mr-2"
          />
          필수 금기사항
        </div>
        <hr class="border-rose-200/60 mb-4" />
        <ul
          class="list-disc pl-5 text-sm font-medium text-rose-700/90 space-y-2"
        >
          <li>안 친한데 가족 대동</li>
        </ul>
      </div>

      <!-- 추천 선물 -->
      <div class="bg-emerald-50/30 rounded-3xl p-6 border border-emerald-100">
        <div class="flex items-center text-emerald-700 font-bold mb-4">
          <font-awesome-icon icon="fa-solid fa-gift" class="h-5 w-5 mr-2" />
          추천 선물 & 팁
        </div>
        <hr class="border-emerald-200/50 mb-4" />
        <ul
          class="list-disc pl-5 text-sm font-medium text-emerald-800/90 space-y-2"
        >
          <li>축의금</li>
        </ul>
      </div>

      <!-- 하단 액션 버튼 -->
      <div class="pt-2 space-y-3">
        <!-- <button
          @click="handleCreateMessage"
          class="w-full bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50 active:scale-[0.99] transition py-4 px-6 rounded-2xl font-bold text-base flex items-center justify-center shadow-sm"
        >
          <font-awesome-icon icon="fa-solid fa-comment" class="h-5 w-5 mr-2" />
          상황별 추천 멘트 만들기
        </button> -->

        <button
          @click="handleChatWithAI"
          class="w-full bg-[#0f1423] text-white hover:bg-slate-800 active:scale-[0.99] transition py-4 px-6 rounded-2xl font-bold text-base flex items-center justify-center shadow-md"
        >
          <font-awesome-icon
            icon="fa-solid fa-wand-magic-sparkles"
            class="h-5 w-5 mr-2 text-indigo-300"
          />
          AI와 더 자세히 대화하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import surveyData from '@/assets/surveyData.json';

const route = useRoute();
const router = useRouter();

const category = computed(() => route.params.category || 'childbirth');
const targetName = computed(() => route.query.targetName || '상대방');
const cultureBase = computed(() => route.query.cultureBase || '미지정');
const categoryName = computed(
  () => surveyData[category.value]?.title || '알 수 없음',
);

const goHome = () => {
  router.push('/');
};

const handleCreateMessage = () => {
  console.log('추천 멘트 만들기 페이지로 이동');
};

const handleChatWithAI = () => {
  router.push({
    name: 'chat',
    query: {
      category: category.value,
      targetName: targetName.value,
      cultureBase: cultureBase.value,
    },
  });
};
</script>

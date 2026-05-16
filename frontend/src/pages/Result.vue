<template>
  <!-- 하단 고정 버튼 때문에 생기는 가림 현상을 방지하기 위해 pb-24 추가 -->
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center p-6 pb-24 font-sans text-slate-800"
  >
    <div class="w-full max-w-md md:max-w-2xl lg:max-w-3xl space-y-6">
      <!-- 상단 네비게이션 -->
      <div class="flex items-center justify-between w-full py-2">
        <button
          @click="goHome"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200 shadow-sm text-slate-600 hover:bg-slate-50 active:scale-95 transition"
          title="처음으로 이동"
        >
          <font-awesome-icon icon="fa-solid fa-house" class="h-5 w-5" />
        </button>
        <span class="text-sm md:text-base font-semibold text-slate-500"
          >진단 결과</span
        >
        <div class="w-10"></div>
      </div>

      <!-- 요약 정보 -->
      <div
        class="bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-slate-100"
      >
        <div class="flex items-center justify-between mb-4">
          <span
            class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-xs md:text-sm font-bold"
          >
            {{ categoryName }}
          </span>
          <span class="text-xs md:text-sm font-bold text-slate-400">
            기준: {{ cultureBase }}
          </span>
        </div>
        <h1
          class="text-xl md:text-2xl lg:text-3xl font-bold text-slate-900 leading-tight"
        >
          <span class="text-indigo-600">{{ targetName }}</span
          >님을 위한<br />
          맞춤 가이드가 도착했습니다.
        </h1>
      </div>

      <!-- 메인 콘텐츠 그리드 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
        <!-- 금액 추천 섹션 -->
        <div
          class="bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-slate-100 flex flex-col justify-center text-center"
        >
          <h2 class="text-sm md:text-base font-medium text-slate-400 mb-2">
            적정 추천 금액
          </h2>
          <div
            class="text-5xl md:text-6xl font-black tracking-tight mb-2 text-slate-900"
          >
            50,000<span class="text-2xl font-bold text-indigo-600 ml-1"
              >원</span
            >
          </div>
          <p class="text-sm md:text-base font-semibold text-slate-400 mb-6">
            최소 30,000원 이상
          </p>

          <div
            class="bg-emerald-50 rounded-2xl p-4 flex items-center justify-start border border-emerald-100"
          >
            <span class="text-emerald-500 mr-2 flex items-center">
              <font-awesome-icon
                icon="fa-solid fa-circle-check"
                class="h-5 w-5"
              />
            </span>
            <p class="text-sm md:text-base font-medium text-slate-600">
              안 가고 3만원 or 가고 5만원
            </p>
          </div>
        </div>

        <!-- 상세 정보 섹션 (금기 & 추천) -->
        <div class="flex flex-col gap-6">
          <!-- 금기사항 -->
          <div
            class="flex-1 bg-rose-50/50 rounded-3xl p-6 border border-rose-100 flex flex-col"
          >
            <div class="flex items-center text-rose-600 font-bold mb-3">
              <font-awesome-icon
                icon="fa-solid fa-triangle-exclamation"
                class="h-5 w-5 mr-2"
              />
              필수 금기사항
            </div>
            <hr class="border-rose-200 mb-4" />
            <ul
              class="list-disc pl-5 text-sm md:text-base font-medium text-rose-800 space-y-2 flex-1"
            >
              <li>안 친한데 가족 대동</li>
            </ul>
          </div>

          <!-- 추천 선물 -->
          <div
            class="flex-1 bg-emerald-50/50 rounded-3xl p-6 border border-emerald-100 flex flex-col"
          >
            <div class="flex items-center text-emerald-700 font-bold mb-3">
              <font-awesome-icon icon="fa-solid fa-gift" class="h-5 w-5 mr-2" />
              추천 선물 & 팁
            </div>
            <hr class="border-emerald-200 mb-4" />
            <ul
              class="list-disc pl-5 text-sm md:text-base font-medium text-emerald-800 space-y-2 flex-1"
            >
              <li>축의금</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 새로 추가된 AI 답변 표시 카드 -->
      <div
        class="bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-slate-100 space-y-4"
      >
        <div
          class="flex items-center text-slate-900 font-bold border-b border-slate-100 pb-3"
        >
          <font-awesome-icon
            icon="fa-solid fa-robot"
            class="h-5 w-5 mr-2 text-indigo-500"
          />
          AI 맞춤 분석 보고서
        </div>

        <!-- 대화/답변 내용이 쭉 표시되는 영역 -->
        <div
          class="space-y-4 text-sm md:text-base leading-relaxed text-slate-600"
        >
          <p>
            안녕하세요! 입력해주신 정보를 바탕으로 분석한 결과, 상대방과의
            관계는
            <span class="font-semibold text-slate-900"
              >"일정 수준의 친분이 있는 지인"</span
            >으로 분류됩니다.
          </p>
          <p>
            해당 문화권(기준: {{ cultureBase }})의 최근 트렌드를 고려했을 때,
            직접 참석이 어려우시다면
            <span class="font-semibold text-indigo-600">3만 원</span>이 가장
            결례가 없는 선이며, 식사 자리에 참석하시는 경우 최소
            <span class="font-semibold text-indigo-600">5만 원</span>을 추천해
            드립니다.
          </p>
          <div
            class="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-xs md:text-sm text-slate-500"
          >
            💡 <span class="font-semibold text-slate-700">추가 팁:</span> 만약
            상대방이 최근 나에게 먼저 경조사를 챙겨준 적이 있다면, 참석 여부와
            관계없이 5만 원 이상으로 상향 조정하는 것이 관계 유지에 유리합니다.
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 고정(Fixed) 액션 버튼 영역 -->
    <div
      class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-50 via-slate-50/90 to-transparent flex justify-center z-50"
    >
      <div class="w-full max-w-md md:max-w-2xl lg:max-w-3xl">
        <button
          @click="handleChatWithAI"
          class="w-full bg-slate-900 text-white hover:bg-slate-800 active:scale-[0.99] transition py-4 px-6 rounded-2xl font-bold text-base md:text-lg flex items-center justify-center shadow-lg"
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

<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-between pt-12 pb-8 px-6 font-sans relative"
  >
    <div class="w-full max-w-md">
      <div class="flex items-center mb-6">
        <button
          @click="router.back()"
          class="mr-4 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2.5"
            stroke="currentColor"
            class="w-5 h-5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15.75 19.5 8.25 12l7.5-7.5"
            />
          </svg>
        </button>
        <div class="flex-1 bg-slate-200 h-1.5 rounded-full overflow-hidden">
          <div
            class="bg-indigo-600 h-1.5 transition-all duration-300"
            :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"
          ></div>
        </div>
      </div>

      <div class="mb-8 text-left">
        <span class="text-xs font-bold text-indigo-600 block mb-1"
          >Q{{ currentStep + 1 }}.</span
        >
        <h1 class="text-2xl font-bold text-slate-900 leading-snug">
          {{ currentQuestion.question }}
        </h1>
      </div>

      <div class="grid grid-cols-1 gap-3 w-full">
        <button
          v-for="(option, idx) in currentQuestion.options"
          :key="idx"
          @click="selectAnswer(option)"
          :class="[
            'w-full bg-white rounded-2xl py-4 px-6 text-left font-bold border text-base transition-all duration-150',
            answers[currentStep] === option
              ? 'border-indigo-600 text-indigo-600 shadow-sm bg-indigo-50/10'
              : 'border-slate-100 text-slate-700 hover:border-slate-200',
          ]"
        >
          {{ option }}
        </button>
      </div>
    </div>

    <div class="w-full max-w-md flex gap-3 mt-8">
      <button
        v-if="currentStep > 0"
        @click="prevStep"
        class="flex-1 bg-slate-200 text-slate-700 font-bold py-4 rounded-3xl active:scale-[0.98] transition-transform"
      >
        이전
      </button>

      <button
        @click="nextStep"
        :disabled="!answers[currentStep]"
        :class="[
          'flex-[2] font-bold py-4 rounded-3xl text-white shadow-lg shadow-indigo-600/20 active:scale-[0.98] transition-all',
          answers[currentStep]
            ? 'bg-indigo-600'
            : 'bg-slate-300 cursor-not-allowed shadow-none',
        ]"
      >
        {{ currentStep === totalSteps - 1 ? '결과 확인하기' : '다음 문항' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import surveyData from '@/assets/surveyData.json';

const route = useRoute();
const router = useRouter();

// 현재 URL 파라미터에서 카테고리 추출 (예: childbirth, wedding, career)
const category = ref(route.params.category || 'childbirth');

// 선택된 카테고리의 전체 데이터 (질문 목록 포함)
const categoryData = computed(() => surveyData[category.value] || { questions: [] });
const questions = computed(() => categoryData.value.questions);
const totalSteps = computed(() => questions.value.length);

// 현재 사용자가 위치한 질문 인덱스 (0부터 시작)
const currentStep = ref(0);
const currentQuestion = computed(() => questions.value[currentStep.value]);

// 사용자가 선택한 답변을 저장할 배열
const answers = ref([]);

// 답변 선택 핸들러
const selectAnswer = (option) => {
  answers.value[currentStep.value] = option;
};

// 이전 버튼
const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--;
};

// 다음 버튼 / 결과 확인
const nextStep = () => {
  if (!answers.value[currentStep.value]) return; // 미선택 시 작동 방지

  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++; // 다음 질문으로 이동
  } else {
    // ⚠️ 모든 질문 완료 -> 결과 페이지로 이동 (State나 쿼리로 데이터 전달 가능)
    router.push({
      name: 'Result',
      params: { category: category.value },
      query: { answers: JSON.stringify(answers.value) },
    });
  }
};
</script>

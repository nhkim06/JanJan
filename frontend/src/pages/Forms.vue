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
          @click="selectAnswerAndNext(option)"
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

    <div class="w-full max-w-md flex flex-col gap-3 mt-8">
      <button
        @click="skipStep"
        class="w-full bg-white border border-slate-200 text-slate-500 font-bold py-3.5 rounded-2xl active:scale-[0.98] transition-all text-sm hover:bg-slate-50"
      >
        이 질문 건너뛰기
      </button>

      <div class="flex gap-3 w-full">
        <button
          v-if="currentStep > 0"
          @click="prevStep"
          class="flex-1 bg-indigo-600 text-white font-bold py-4 rounded-3xl active:scale-[0.98] transition-transform text-base"
        >
          이전
        </button>

        <div v-else class="flex-1"></div>

        <button
          @click="nextStep"
          :disabled="!answers[currentStep]"
          :class="[
            'flex-1 font-bold py-4 rounded-3xl text-white shadow-lg active:scale-[0.98] transition-all text-base',
            answers[currentStep]
              ? 'bg-indigo-600 shadow-indigo-600/20'
              : 'bg-slate-300 cursor-not-allowed shadow-none',
          ]"
        >
          {{ currentStep === totalSteps - 1 ? '결과 확인하기' : '다음' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import surveyData from '@/assets/surveyData.json';

const route = useRoute();
const router = useRouter();

const category = ref(route.params.category || 'childbirth');

const categoryData = computed(
  () => surveyData[category.value] || { questions: [] },
);
const questions = computed(() => categoryData.value.questions);
const totalSteps = computed(() => questions.value.length);

const currentStep = ref(0);
const currentQuestion = computed(() => questions.value[currentStep.value]);

const answers = ref([]);

// 선택 목록 클릭 시 작동
const selectAnswerAndNext = (option) => {
  answers.value[currentStep.value] = option;

  // 시각적 피드백용 미세 딜레이
  setTimeout(() => {
    nextStep();
  }, 150);
};

// 1. [요구사항] 건너뛰기 시 기존 선택 해제 후 다음 단계로
const skipStep = () => {
  answers.value[currentStep.value] = null; // 선택했던 항목을 null로 밀어버려 해제함
  nextStep();
};

// 이전 버튼
const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--;
};

// 다음 버튼 / 결과 확인 처리 공통 로직
const nextStep = () => {
  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++;
  } else {
    router.push({
      name: 'Result',
      params: { category: category.value },
      query: { answers: JSON.stringify(answers.value) },
    });
  }
};
</script>

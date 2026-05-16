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

        <button
          @click="selectDontKnowAndNext"
          :class="[
            'w-full bg-white rounded-2xl py-4 px-6 text-left font-bold border text-base transition-all duration-150',
            answers[currentStep] === '모르겠음'
              ? 'border-indigo-600 text-indigo-600 shadow-sm bg-indigo-50/10'
              : 'border-slate-100 text-slate-400 hover:border-slate-200 bg-slate-50/30 font-medium',
          ]"
        >
          모르겠음
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
          @click="prevStep"
          :disabled="currentStep === 0"
          :class="[
            'flex-1 font-bold py-4 rounded-3xl transition-all text-base border',
            currentStep === 0
              ? 'bg-slate-100 text-slate-300 border-slate-200 cursor-not-allowed shadow-none'
              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 active:scale-[0.98]',
          ]"
        >
          이전
        </button>

        <button
          @click="nextStep"
          :disabled="answers[currentStep] === undefined"
          :class="[
            'flex-1 font-bold py-4 rounded-3xl text-white shadow-lg active:scale-[0.98] transition-all text-base',
            answers[currentStep] !== undefined
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

// 일반 선택 목록 클릭 시 작동
const selectAnswerAndNext = (option) => {
  answers.value[currentStep.value] = option;
  setTimeout(() => {
    nextStep();
  }, 150);
};

// [요구사항] '모르겠음' 선택 시 건너뛰기와 동일하게 처리
const selectDontKnowAndNext = () => {
  // 1. 내부 상태를 '모르겠음' 문자열로 주어 UI 체크 표시 유지용 피드백 제공 후 넘어갈 때 null 처리
  answers.value[currentStep.value] = '모르겠음';

  setTimeout(() => {
    // 2. 건너뛰기 로직인 null 처리를 한 뒤 다음 단계로 전송
    answers.value[currentStep.value] = null;
    nextStep();
  }, 150);
};

// 건너뛰기 기능 (답변을 null로 밀어버림)
const skipStep = () => {
  answers.value[currentStep.value] = null;
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

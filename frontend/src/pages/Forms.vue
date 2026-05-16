<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-between pt-12 pb-8 px-6 font-sans relative"
  >
    <div class="w-full max-w-md md:max-w-2xl">
      <!-- 상단 헤더: 뒤로가기 & 프로그레스 바 -->
      <div class="flex items-center mb-10">
        <button
          @click="handleExit"
          class="mr-4 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-10 h-10 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" />
        </button>
        <div class="flex-1 bg-slate-200 h-1.5 rounded-full overflow-hidden">
          <div
            class="bg-indigo-600 h-1.5 transition-all duration-300"
            :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- [사전 단계 1] 상대방 이름 입력 -->
      <div v-if="currentStep === 0" class="mb-8 text-left md:text-center">
        <span class="text-xs md:text-sm font-bold text-indigo-600 block mb-1"
          >기본 정보 입력</span
        >
        <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 leading-snug mb-8">
          상대방의<br class="md:hidden" /> 이름을 입력해주세요
        </h1>
        <div class="max-w-xl mx-auto">
          <input
            v-model="preSurveyData.targetName"
            type="text"
            placeholder="예: 홍길동, 김대리님"
            class="w-full bg-white border border-slate-200 rounded-2xl py-4 md:py-5 px-5 md:px-8 text-base md:text-lg font-bold text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 shadow-sm"
            @keyup.enter="!isNextDisabled && handleNext()"
          />
        </div>
      </div>

      <!-- [사전 단계 2] 문화권 선택 -->
      <div v-else-if="currentStep === 1" class="mb-8 text-left md:text-center">
        <span class="text-xs md:text-sm font-bold text-indigo-600 block mb-1"
          >기준 설정</span
        >
        <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 leading-snug mb-8">
          어느 문화권 기준으로<br class="md:hidden" /> 판단할까요?
        </h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-xl mx-auto">
          <button
            v-for="culture in ['한국', '일본', '둘 다', '아직 모르겠음']"
            :key="culture"
            @click="selectCulture(culture)"
            :class="[
              'w-full bg-white rounded-2xl py-4 md:py-5 px-6 text-left md:text-center font-bold border text-base md:text-lg transition-all duration-150 shadow-sm',
              preSurveyData.cultureBase === culture
                ? 'border-indigo-600 text-indigo-600 bg-indigo-50/10'
                : 'border-slate-100 text-slate-700 hover:border-slate-200',
            ]"
          >
            {{ culture }}
          </button>
        </div>
      </div>

      <!-- [메인 단계] 설문 문항 루프 (currentStep >= 2) -->
      <div v-else-if="currentQuestion" class="w-full max-w-xl mx-auto">
        <div class="mb-8 text-left md:text-center">
          <span class="text-xs md:text-sm font-bold text-indigo-600 block mb-1">
            Q{{ currentStep - 1 }}.
          </span>
          <h1 class="text-2xl md:text-3xl font-bold text-slate-900 leading-snug">
            {{ currentQuestion.question }}
          </h1>
        </div>

        <div class="grid grid-cols-1 gap-3 w-full">
          <button
            v-for="(option, idx) in currentQuestion.options"
            :key="idx"
            @click="selectAnswer(option)"
            :class="[
              'w-full bg-white rounded-2xl py-4 md:py-5 px-6 text-left md:text-center font-bold border text-base md:text-lg transition-all duration-150 shadow-sm',
              answers[surveyQuestionIdx] === option
                ? 'border-indigo-600 text-indigo-600 bg-indigo-50/10'
                : 'border-slate-100 text-slate-700 hover:border-slate-200',
            ]"
          >
            {{ option }}
          </button>

          <button
            @click="selectAnswer('모르겠음')"
            :class="[
              'w-full bg-white rounded-2xl py-4 md:py-5 px-6 text-left md:text-center font-bold border text-base md:text-lg transition-all duration-150 shadow-sm',
              answers[surveyQuestionIdx] === '모르겠음'
                ? 'border-indigo-600 text-indigo-600 bg-indigo-50/10'
                : 'border-slate-100 text-slate-700 hover:border-slate-200',
            ]"
          >
            모르겠음
          </button>
        </div>
      </div>
    </div>

    <!-- 하단 제어 버튼 컴포넌트 -->
    <div class="w-full max-w-md md:max-w-xl flex flex-col gap-3 mt-8">
      <div class="flex gap-3 w-full">
        <button
          @click="handlePrev"
          :disabled="currentStep === 0"
          :class="[
            'flex-1 font-bold py-4 md:py-5 rounded-3xl transition-all text-base md:text-lg border bg-white text-slate-700 border-slate-200 hover:bg-slate-50 active:scale-[0.98]',
            currentStep === 0 ? 'opacity-50 cursor-not-allowed' : '',
          ]"
        >
          이전
        </button>

        <button
          @click="handleNext"
          :disabled="isNextDisabled"
          :class="[
            'flex-1 font-bold py-4 md:py-5 rounded-3xl text-white shadow-lg active:scale-[0.98] transition-all text-base md:text-lg',
            !isNextDisabled
              ? 'bg-indigo-600 shadow-indigo-600/20'
              : 'bg-slate-300 text-slate-400 cursor-not-allowed shadow-none',
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
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

// 카테고리 설정
const category = ref(route.params.category || 'birth');

// JSON 데이터 파싱 및 인덱싱 처리
const categoryData = computed(
  () => surveyData[category.value] || { questions: [] },
);
const questions = computed(() => categoryData.value.questions);

// 전체 스텝 수 계산 (사전정보 2단계 + 실제 질문 리스트 개수)
const totalSteps = computed(() => questions.value.length + 2);

// 전역 단일 스텝 포인터 (0: 이름, 1: 문화권, 2 이상: 실제 질문)
const currentStep = ref(0);

// 실제 질문 데이터 매핑을 위한 가상 계산 인덱스
const surveyQuestionIdx = computed(() => currentStep.value - 2);
const currentQuestion = computed(
  () => questions.value[surveyQuestionIdx.value] || null,
);

// 데이터 적재용 반응형 변수들
const preSurveyData = ref({
  targetName: '',
  cultureBase: '',
});
const answers = ref([]);

// 다음 버튼 Validation 조건 관리
const isNextDisabled = computed(() => {
  if (currentStep.value === 0) return !preSurveyData.value.targetName.trim();
  if (currentStep.value === 1) return !preSurveyData.value.cultureBase;
  if (currentStep.value >= 2) {
    return answers.value[surveyQuestionIdx.value] === undefined;
  }
  return false;
});

// 문화권 옵션 선택 핸들러 (사전 정보는 편의상 자동 이동 유지)
const selectCulture = (culture) => {
  preSurveyData.value.cultureBase = culture;
  setTimeout(() => {
    handleNext();
  }, 150);
};

// 메인 설문 답변 선택 핸들러
const selectAnswer = (option) => {
  answers.value[surveyQuestionIdx.value] = option;

  // 마지막 질문 단계가 아닐 때만 150ms 뒤 자동으로 다음 스텝 이동
  if (currentStep.value < totalSteps.value - 1) {
    setTimeout(() => {
      handleNext();
    }, 150);
  }
  // 마지막 단계라면 데이터 상태(하이라이트)만 변경하고 가만히 멈춤 -> 유저가 하단 버튼을 직접 눌러야 함
};

// 상단 헤더 좌측 버튼: 이탈 처리
const handleExit = () => {
  router.back();
};

// 하단 [이전] 버튼
const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

// [다음 / 결과확인] 제어 버튼 및 페이지 이동 처리 통합
const handleNext = async () => {
  if (isNextDisabled.value) return;

  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++;
  } else {
    // 최종 제출 시점 데이터 가공
    const formattedAnswers = questions.value.map((q, idx) => ({
      question: q.question,
      answer: answers.value[idx] === '모르겠음' ? null : answers.value[idx]
    }));

    try {
      const response = await apiClient.post('/form/new', {
        answers: formattedAnswers,
        targetName: preSurveyData.value.targetName,
        cultureBase: preSurveyData.value.cultureBase
      });

      if (response.data.success) {
        router.push({
          name: 'result',
          params: { category: category.value },
          query: {
            targetName: preSurveyData.value.targetName,
            cultureBase: preSurveyData.value.cultureBase,
            roomId: response.data.formId
          },
        });
      }
    } catch (error) {
      console.error('폼 저장 에러:', error);
      alert('데이터 저장 중 오류가 발생했습니다.');
    }
  }
};
</script>

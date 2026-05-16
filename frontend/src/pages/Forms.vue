<template>
  <div
    class="min-h-screen bg-slate-50 flex flex-col items-center justify-between pt-12 pb-8 px-6 font-sans relative"
  >
    <div class="w-full max-w-md md:max-w-2xl">
      <!-- Top Header: Back & Progress Bar -->
      <div class="flex items-center justify-between mb-8">
        <button
          @click="handleExit"
          class="w-10 h-10 flex items-center justify-center bg-white rounded-full border border-slate-200 shadow-sm text-slate-500 hover:text-slate-800 transition"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" class="h-4 w-4" />
        </button>
        <div class="flex-1 mx-6 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-indigo-600 transition-all duration-500 ease-out"
            :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"
          ></div>
        </div>
        <div class="text-[11px] font-black text-slate-400 uppercase tracking-tighter">
          Step {{ currentStep + 1 }}/{{ totalSteps }}
        </div>
      </div>

      <!-- Main Question Area -->
      <div class="space-y-10">
        <!-- 0. Name Input Step -->
        <div v-if="currentStep === 0" class="space-y-6">
          <h2 class="text-2xl md:text-3xl font-black text-slate-900 leading-tight">
            Who is the person<br />related to this event?
          </h2>
          <div class="relative">
            <input
              v-model="preSurveyData.targetName"
              type="text"
              placeholder="Enter name (e.g. John Doe)"
              class="w-full bg-transparent border-b-2 border-slate-200 py-4 text-xl md:text-2xl font-bold text-indigo-600 placeholder-slate-300 focus:outline-none focus:border-indigo-600 transition-all"
              @keyup.enter="handleNext"
            />
          </div>
        </div>

        <!-- 1. Culture Choice Step -->
        <div v-else-if="currentStep === 1" class="space-y-6">
          <h2 class="text-2xl md:text-3xl font-black text-slate-900 leading-tight">
            Which cultural background<br />should I consider?
          </h2>
          <div class="grid grid-cols-1 gap-3">
            <button
              v-for="culture in ['Korea', 'Japan', 'Global']"
              :key="culture"
              @click="selectCulture(culture)"
              class="w-full p-5 rounded-2xl border-2 text-left transition-all flex justify-between items-center group"
              :class="
                preSurveyData.cultureBase === culture
                  ? 'border-indigo-600 bg-indigo-50/50 shadow-md shadow-indigo-100'
                  : 'border-white bg-white hover:border-slate-100 shadow-sm'
              "
            >
              <span
                class="text-base md:text-lg font-bold"
                :class="
                  preSurveyData.cultureBase === culture ? 'text-indigo-700' : 'text-slate-600'
                "
              >
                {{ culture }}
              </span>
              <div
                class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
                :class="
                  preSurveyData.cultureBase === culture
                    ? 'border-indigo-600 bg-indigo-600 text-white'
                    : 'border-slate-100 bg-slate-50'
                "
              >
                <font-awesome-icon
                  v-if="preSurveyData.cultureBase === culture"
                  icon="fa-solid fa-check"
                  class="w-3 h-3"
                />
              </div>
            </button>
          </div>
        </div>

        <!-- 2+. Survey Questions -->
        <div v-else-if="currentQuestion" class="space-y-6">
          <h2 class="text-2xl md:text-3xl font-black text-slate-900 leading-tight">
            {{ currentQuestion.question }}
          </h2>
          <div class="grid grid-cols-1 gap-3">
            <button
              v-for="option in currentQuestion.options"
              :key="option"
              @click="selectAnswer(option)"
              class="w-full p-5 rounded-2xl border-2 text-left transition-all flex justify-between items-center group"
              :class="
                answers[surveyQuestionIdx] === option
                  ? 'border-indigo-600 bg-indigo-50/50 shadow-md shadow-indigo-100'
                  : 'border-white bg-white hover:border-slate-100 shadow-sm'
              "
            >
              <span
                class="text-base md:text-lg font-bold"
                :class="
                  answers[surveyQuestionIdx] === option ? 'text-indigo-700' : 'text-slate-600'
                "
              >
                {{ option }}
              </span>
              <div
                class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
                :class="
                  answers[surveyQuestionIdx] === option
                    ? 'border-indigo-600 bg-indigo-600 text-white'
                    : 'border-slate-100 bg-slate-50'
                "
              >
                <font-awesome-icon
                  v-if="answers[surveyQuestionIdx] === option"
                  icon="fa-solid fa-check"
                  class="w-3 h-3"
                />
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Action Area -->
    <div class="w-full max-w-md md:max-w-2xl flex flex-col space-y-4">
      <div class="flex space-x-3">
        <button
          v-if="currentStep > 0"
          @click="handlePrev"
          class="flex-1 py-5 rounded-3xl font-black text-slate-400 hover:text-slate-600 transition-colors"
        >
          Previous
        </button>
        <button
          @click="handleNext"
          :disabled="isNextDisabled"
          class="flex-[2] py-5 rounded-3xl font-black text-lg shadow-xl transition-all active:scale-[0.98]"
          :class="
            isNextDisabled
              ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
              : 'bg-indigo-600 text-white shadow-indigo-200 hover:bg-indigo-700'
          "
        >
          {{ currentStep === totalSteps - 1 ? 'Show Analysis' : 'Next' }}
        </button>
      </div>
    </div>

    <!-- Submission Loading Overlay -->
    <div v-if="isSubmitting" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm">
       <div class="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
       <p class="text-slate-600 font-bold text-lg">Analyzing results...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import surveyData from '@/assets/surveyData.json';
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

const category = ref(route.params.category as string || 'birth');

const categoryData = computed(
  () => (surveyData as any)[category.value] || { questions: [] },
);
const questions = computed(() => categoryData.value.questions);

const totalSteps = computed(() => questions.value.length + 2);

const currentStep = ref(0);

const surveyQuestionIdx = computed(() => currentStep.value - 2);
const currentQuestion = computed(
  () => questions.value[surveyQuestionIdx.value] || null,
);

const preSurveyData = ref({
  targetName: '',
  cultureBase: '',
});
const answers = ref<any[]>([]);
const isSubmitting = ref(false);

const isNextDisabled = computed(() => {
  if (isSubmitting.value) return true;
  if (currentStep.value === 0) return !preSurveyData.value.targetName.trim();
  if (currentStep.value === 1) return !preSurveyData.value.cultureBase;
  if (currentStep.value >= 2) {
    return answers.value[surveyQuestionIdx.value] === undefined;
  }
  return false;
});

const selectCulture = (culture: string) => {
  preSurveyData.value.cultureBase = culture;
  setTimeout(() => {
    handleNext();
  }, 150);
};

const selectAnswer = (option: string) => {
  answers.value[surveyQuestionIdx.value] = option;
  if (currentStep.value < totalSteps.value - 1) {
    setTimeout(() => {
      handleNext();
    }, 150);
  }
};

const handleExit = () => {
  router.back();
};

const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

const handleNext = async () => {
  if (isNextDisabled.value) return;

  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++;
  } else {
    try {
      isSubmitting.value = true;
      const formattedAnswers = questions.value.map((q: any, idx: number) => ({
        question: q.question,
        answer: answers.value[idx] === 'Not sure' || answers.value[idx] === '모르겠음' ? null : answers.value[idx],
      }));

      const response = await apiClient.post('/form/new', {
        answers: formattedAnswers,
        targetName: preSurveyData.value.targetName,
        cultureBase: preSurveyData.value.cultureBase,
        category: category.value
      });

      if (response.data.success) {
        router.push({
          name: 'result',
          params: { category: category.value },
          query: {
            targetName: preSurveyData.value.targetName,
            cultureBase: preSurveyData.value.cultureBase,
            roomId: response.data.formId,
          },
        });
      }
    } catch (error) {
      console.error('Error saving form:', error);
      alert('An error occurred while saving data.');
    } finally {
      isSubmitting.value = false;
    }
  }
};
</script>

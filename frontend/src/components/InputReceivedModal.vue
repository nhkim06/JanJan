<script setup>
import { ref, watch, computed } from 'vue';
import eventData from '../assets/events.json';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'submit']);

// 카테고리 데이터 가공
const categoriesByGroup = computed(() => {
  const result = {};
  for (const key in eventData) {
    result[key] = eventData[key].options.map((opt) => opt.title);
  }
  return result;
});

// 입력 폼 상태 관리
const isReceived = ref(true); // true: 받은 것, false: 준 것
const eventType = ref('축하');
const personName = ref('');
const selectedCategory = ref('');
const eventDate = ref('');
const amount = ref('');
const currency = ref('KRW'); // 통화 상태 추가 ('KRW', 'USD', 'JPY')

// 통화 기호 매핑 함수
const currencySymbol = computed(() => {
  if (currency.value === 'USD') return '$';
  if (currency.value === 'JPY') return '¥';
  return '₩';
});

// 구분(축하/위로)이 바뀔 때마다 상세 카테고리 초기화
watch(eventType, (newType) => {
  if (categoriesByGroup.value[newType]) {
    selectedCategory.value = categoriesByGroup.value[newType][0];
  }
});

// 모달이 열릴 때마다 폼 기본값 초기화
watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      isReceived.value = true;
      eventType.value = '축하';
      personName.value = '';
      currency.value = 'KRW'; // 통화 기본값 원화로 초기화
      if (categoriesByGroup.value['축하']) {
        selectedCategory.value = categoriesByGroup.value['축하'][0];
      }
      eventDate.value = new Date().toISOString().substring(0, 10);
      amount.value = '';
    }
  },
);

// 천단위 콤마 포맷팅 (달러 소수점 등 복잡한 계산 배제하고 순수 숫자 콤마 유지)
const formatAmount = (e) => {
  let value = e.target.value.replace(/[^0-9]/g, '');
  if (value) {
    amount.value = Number(value).toLocaleString();
  } else {
    amount.value = '';
  }
};

const handleClose = () => {
  emit('close');
};

const handleSubmit = () => {
  if (!personName.value.trim()) {
    alert('이름을 입력해주세요.');
    return;
  }
  if (!selectedCategory.value) {
    alert('카테고리를 선택해주세요.');
    return;
  }
  if (!eventDate.value) {
    alert('날짜를 선택해주세요.');
    return;
  }
  if (!amount.value) {
    alert('금액을 입력해주세요.');
    return;
  }

  // 데이터 전송 포맷 매핑
  emit('submit', {
    targetName: personName.value.trim(),
    received: isReceived.value,
    value: Number(amount.value.replace(/,/g, '')),
    currency: currency.value, // cultureBase 대신 변경된 currency 데이터 전송
    category: selectedCategory.value,
    date: eventDate.value,
  });
};
</script>

<template>
  <Transition name="fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-50 flex items-center justify-center p-4 select-none"
      @click.self="handleClose"
    >
      <Transition name="zoom">
        <div
          v-if="isOpen"
          class="w-full max-w-md bg-white rounded-[1.75rem] shadow-2xl border border-slate-200/50 flex flex-col overflow-hidden relative"
        >
          <!-- 상단 장식 바 (모바일 느낌) -->
          <div
            class="h-1 w-10 bg-slate-200 rounded-full mx-auto mt-2.5 mb-0.5 sm:hidden"
          ></div>

          <!-- 헤더 -->
          <div class="px-6 pt-4 pb-1 flex items-center justify-between">
            <div>
              <h2
                class="text-xl font-black text-slate-900 tracking-tight mt-0.5"
              >
                경조사 기록
              </h2>
              <p class="text-[12px] font-medium text-slate-400 mt-0.5">
                잊지 않도록 소중한 마음을 기록하세요
              </p>
            </div>
            <button
              @click="handleClose"
              class="w-9 h-9 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all duration-200 active:scale-90"
            >
              <font-awesome-icon icon="fa-solid fa-xmark" class="w-4 h-4" />
            </button>
          </div>

          <!-- 폼 영역 -->
          <div class="px-6 py-4 space-y-4 flex-1 overflow-y-auto max-h-[70vh]">
            <!-- [추가] 1. 주고받음 구분 선택 (received 데이터 바인딩) -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >구분 선택</label
              >
              <div
                class="grid grid-cols-2 gap-2.5 p-1 bg-slate-100/80 rounded-xl"
              >
                <button
                  type="button"
                  @click="isReceived = true"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    isReceived
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-arrow-down"
                    class="w-3 h-3 text-indigo-500"
                    v-if="isReceived"
                  />
                  <span>받았어요 (수령)</span>
                </button>
                <button
                  type="button"
                  @click="isReceived = false"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    !isReceived
                      ? 'bg-white text-green-600 shadow-[0_2px_8px_rgba(244,63,94,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-arrow-up"
                    class="w-3 h-3 text-green-500"
                    v-if="!isReceived"
                  />
                  <span>보냈어요 (지출)</span>
                </button>
              </div>
            </div>

            <!-- 2. 이름 입력 (구분에 따라 라벨/플레이스홀더 변경) -->
            <div class="space-y-1.5">
              <label
                for="event-name"
                class="block text-[12px] font-bold text-slate-500 ml-1"
              >
                {{ isReceived ? '보낸 사람 이름' : '받는 사람 이름' }}
              </label>
              <input
                id="event-name"
                type="text"
                v-model="personName"
                :placeholder="
                  isReceived
                    ? '선물이나 부조를 준 사람의 이름'
                    : '받는 사람의 이름'
                "
                class="w-full px-4 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-bold text-slate-700 placeholder-slate-300 outline-none transition-all"
              />
            </div>

            <!-- 3. 경조사 대분류 구분 -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >유형 선택</label
              >
              <div
                class="grid grid-cols-2 gap-2.5 p-1 bg-slate-100/80 rounded-xl"
              >
                <button
                  type="button"
                  @click="eventType = '축하'"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    eventType === '축하'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-gift"
                    :class="[
                      'w-3.5 h-3.5',
                      eventType === '축하' ? 'text-indigo-500' : '',
                    ]"
                  />
                  <span>축하하기</span>
                </button>
                <button
                  type="button"
                  @click="eventType = '위로'"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    eventType === '위로'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(72,187,120,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-bandage"
                    :class="[
                      'w-3.5 h-3.5',
                      eventType === '위로' ? 'text-indigo-500' : '',
                    ]"
                  />
                  <span>위로하기</span>
                </button>
              </div>
            </div>

            <!-- 4. 상세 카테고리 -->
            <div class="space-y-1.5">
              <label
                for="event-category"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >상세 항목</label
              >
              <div class="relative group">
                <select
                  id="event-category"
                  v-model="selectedCategory"
                  class="w-full px-4 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-bold text-slate-700 outline-none transition-all appearance-none cursor-pointer group-hover:bg-slate-100/50"
                >
                  <option
                    v-for="cat in categoriesByGroup[eventType]"
                    :key="cat"
                    :value="cat"
                  >
                    {{ cat }}
                  </option>
                </select>
                <div
                  class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-300 group-hover:text-slate-400 transition-colors"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-chevron-down"
                    class="w-3 h-3"
                  />
                </div>
              </div>
            </div>

            <!-- 5. 날짜 선택 -->
            <div class="space-y-1.5">
              <label
                for="event-date"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >날짜</label
              >
              <input
                id="event-date"
                type="date"
                v-model="eventDate"
                class="w-full px-4 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-bold text-slate-700 outline-none transition-all"
              />
            </div>

            <!-- 6. 금액 입력 -->
            <div class="space-y-1.5">
              <label
                for="event-amount"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >금액</label
              >
              <div class="relative flex items-center group">
                <input
                  id="event-amount"
                  type="text"
                  :value="amount"
                  @input="formatAmount"
                  placeholder="0"
                  class="w-full pl-4 pr-12 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-black text-slate-800 placeholder-slate-300 outline-none transition-all text-right group-hover:bg-slate-100/50"
                />
                <!-- 우측 기호 변경 (KRW: ₩, USD: $, JPY: ¥) -->
                <span
                  class="absolute right-4 text-[13px] font-bold text-slate-400"
                  >{{ currencySymbol }}</span
                >
              </div>
            </div>

            <!-- 7. 통화 선택 (금액 밑에 배치, 3열 레이아웃) -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >통화 선택</label
              >
              <div
                class="grid grid-cols-3 gap-2 p-1 bg-slate-100/80 rounded-xl"
              >
                <button
                  type="button"
                  @click="currency = 'KRW'"
                  :class="[
                    'py-2 text-[12px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1',
                    currency === 'KRW'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <span>₩ 원화</span>
                </button>
                <button
                  type="button"
                  @click="currency = 'USD'"
                  :class="[
                    'py-2 text-[12px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1',
                    currency === 'USD'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <span>$ 달러</span>
                </button>
                <button
                  type="button"
                  @click="currency = 'JPY'"
                  :class="[
                    'py-2 text-[12px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1',
                    currency === 'JPY'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <span>¥ 엔화</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 하단 버튼 -->
          <div class="px-6 pb-5 pt-1">
            <button
              type="button"
              @click="handleSubmit"
              class="w-full py-4 text-[15px] font-black text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-lg shadow-slate-200 transition-all duration-300 active:scale-[0.97] flex items-center justify-center space-x-1.5"
            >
              <span>저장하기</span>
              <font-awesome-icon icon="fa-solid fa-check" class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<style scoped>
/* 기존 스타일 그대로 유지 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.zoom-enter-active {
  transition:
    transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.3s ease;
}
.zoom-leave-active {
  transition:
    transform 0.3s cubic-bezier(0.4, 0, 1, 1),
    opacity 0.2s ease;
}
.zoom-enter-from,
.zoom-leave-to {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}

input[type='date']::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.overflow-y-auto::-webkit-scrollbar {
  display: none;
}

.overflow-y-auto {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

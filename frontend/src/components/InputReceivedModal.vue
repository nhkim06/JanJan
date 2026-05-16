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

// Process category data based on events.json
const categoriesByGroup = computed(() => {
  const result = {};
  for (const key in eventData) {
    // key will be "Celebration" or "Condolence"
    result[key] = eventData[key].options.map((opt) => opt.title);
  }
  return result;
});

// Input form state management
const isReceived = ref(true); // true: received, false: sent
const eventType = ref('Celebration');
const personName = ref('');
const selectedCategory = ref('');
const eventDate = ref('');
const amount = ref('');
const currency = ref('KRW'); // Currency state ('KRW', 'USD', 'JPY')

// Currency symbol mapping
const currencySymbol = computed(() => {
  if (currency.value === 'USD') return '$';
  if (currency.value === 'JPY') return '¥';
  return '₩';
});

// Reset detail category whenever eventType changes
watch(eventType, (newType) => {
  if (categoriesByGroup.value[newType]) {
    selectedCategory.value = categoriesByGroup.value[newType][0];
  }
});

// Reset form defaults whenever modal opens
watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      isReceived.value = true;
      eventType.value = 'Celebration';
      personName.value = '';
      currency.value = 'KRW';
      if (categoriesByGroup.value['Celebration']) {
        selectedCategory.value = categoriesByGroup.value['Celebration'][0];
      }
      eventDate.value = new Date().toISOString().substring(0, 10);
      amount.value = '';
    }
  },
);

// Format amount with thousands separator
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
    alert('Please enter a name.');
    return;
  }
  if (!selectedCategory.value) {
    alert('Please select a category.');
    return;
  }
  if (!eventDate.value) {
    alert('Please select a date.');
    return;
  }
  if (!amount.value) {
    alert('Please enter an amount.');
    return;
  }

  // Map to data transfer format
  emit('submit', {
    targetName: personName.value.trim(),
    received: isReceived.value,
    value: Number(amount.value.replace(/,/g, '')),
    currency: currency.value,
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
          <!-- Top decorative bar (mobile feel) -->
          <div
            class="h-1 w-10 bg-slate-200 rounded-full mx-auto mt-2.5 mb-0.5 sm:hidden"
          ></div>

          <!-- Header -->
          <div class="px-6 pt-4 pb-1 flex items-center justify-between">
            <div>
              <h2
                class="text-xl font-black text-slate-900 tracking-tight mt-0.5"
              >
                Event Record
              </h2>
              <p class="text-[12px] font-medium text-slate-400 mt-0.5">
                Keep track of your precious moments
              </p>
            </div>
            <button
              @click="handleClose"
              class="w-9 h-9 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all duration-200 active:scale-90"
            >
              <font-awesome-icon icon="fa-solid fa-xmark" class="w-4 h-4" />
            </button>
          </div>

          <!-- Form Area -->
          <div class="px-6 py-4 space-y-4 flex-1 overflow-y-auto max-h-[70vh]">
            <!-- 1. Type Selection (Received/Sent) -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >Transaction Type</label
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
                  <span>Received</span>
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
                  <span>Sent</span>
                </button>
              </div>
            </div>

            <!-- 2. Name Input -->
            <div class="space-y-1.5">
              <label
                for="event-name"
                class="block text-[12px] font-bold text-slate-500 ml-1"
              >
                {{ isReceived ? 'Sender Name' : 'Recipient Name' }}
              </label>
              <input
                id="event-name"
                type="text"
                v-model="personName"
                :placeholder="
                  isReceived
                    ? 'Who gave this to you?'
                    : 'Who are you giving this to?'
                "
                class="w-full px-4 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-bold text-slate-700 placeholder-slate-300 outline-none transition-all"
              />
            </div>

            <!-- 3. Event Category Selection -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >Occasion Type</label
              >
              <div
                class="grid grid-cols-2 gap-2.5 p-1 bg-slate-100/80 rounded-xl"
              >
                <button
                  type="button"
                  @click="eventType = 'Celebration'"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    eventType === 'Celebration'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-gift"
                    :class="[
                      'w-3.5 h-3.5',
                      eventType === 'Celebration' ? 'text-indigo-500' : '',
                    ]"
                  />
                  <span>Celebration</span>
                </button>
                <button
                  type="button"
                  @click="eventType = 'Condolence'"
                  :class="[
                    'py-2.5 text-[13px] font-bold rounded-lg transition-all duration-300 flex items-center justify-center space-x-1.5',
                    eventType === 'Condolence'
                      ? 'bg-white text-indigo-600 shadow-[0_2px_8px_rgba(72,187,120,0.08)] border border-white'
                      : 'text-slate-400 hover:text-slate-500',
                  ]"
                >
                  <font-awesome-icon
                    icon="fa-solid fa-bandage"
                    :class="[
                      'w-3.5 h-3.5',
                      eventType === 'Condolence' ? 'text-indigo-500' : '',
                    ]"
                  />
                  <span>Condolence</span>
                </button>
              </div>
            </div>

            <!-- 4. Detail Category -->
            <div class="space-y-1.5">
              <label
                for="event-category"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >Event Detail</label
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

            <!-- 5. Date Selection -->
            <div class="space-y-1.5">
              <label
                for="event-date"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >Date</label
              >
              <input
                id="event-date"
                type="date"
                v-model="eventDate"
                class="w-full px-4 py-3.5 bg-slate-50 border-2 border-transparent focus:border-indigo-100 rounded-xl text-[14px] font-bold text-slate-700 outline-none transition-all"
              />
            </div>

            <!-- 6. Amount Input -->
            <div class="space-y-1.5">
              <label
                for="event-amount"
                class="block text-[12px] font-bold text-slate-500 ml-1"
                >Amount</label
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
                <span
                  class="absolute right-4 text-[13px] font-bold text-slate-400"
                  >{{ currencySymbol }}</span
                >
              </div>
            </div>

            <!-- 7. Currency Choice -->
            <div class="space-y-1.5">
              <label class="block text-[12px] font-bold text-slate-500 ml-1"
                >Currency</label
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
                  <span>₩ KRW</span>
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
                  <span>$ USD</span>
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
                  <span>¥ JPY</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Bottom Button -->
          <div class="px-6 pb-5 pt-1">
            <button
              type="button"
              @click="handleSubmit"
              class="w-full py-4 text-[15px] font-black text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-lg shadow-slate-200 transition-all duration-300 active:scale-[0.97] flex items-center justify-center space-x-1.5"
            >
              <span>Save Record</span>
              <font-awesome-icon icon="fa-solid fa-check" class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<style scoped>
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

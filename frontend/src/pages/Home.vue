<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <div class="flex flex-col h-full space-y-8">
        <header class="md:text-center md:mb-4">
          <h1
            class="text-2xl md:text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight mb-2"
          >
            어떤 상황인가요?
          </h1>
          <p class="text-sm md:text-base font-medium text-slate-500/90">
            적정 축의금/부의금을 확인해보세요.
          </p>
        </header>

        <section class="max-w-xl mx-auto w-full">
          <div
            class="flex items-center bg-white rounded-full px-4 py-3 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative group transition-all duration-300 focus-within:shadow-[0_8px_30px_rgb(99,102,241,0.08)]"
          >
            <div
              class="w-9 h-9 bg-gradient-to-tr from-indigo-600 to-violet-500 rounded-full flex items-center justify-center text-white shadow-md shadow-indigo-200"
            >
              <font-awesome-icon
                icon="fa-solid fa-wand-magic-sparkles"
                class="w-4 h-4"
              />
            </div>
            <input
              type="text"
              placeholder="AI에게 바로 물어보기..."
              class="flex-1 bg-transparent border-none outline-none pl-3 text-sm md:text-base font-medium text-slate-700 placeholder-slate-300"
            />
            <button
              class="text-indigo-500 hover:text-indigo-600 active:scale-90 transition-transform p-1"
            >
              <font-awesome-icon
                icon="fa-solid fa-paper-plane"
                class="w-5 h-5 rotate-45"
              />
            </button>
          </div>
        </section>

        <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 축하 버튼 -->
          <button
            @click="router.push('/events/축하')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1"
              >
                축하
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">
                결혼, 승진, 출산 등
              </p>
            </div>
            <div
              class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100"
            >
              <font-awesome-icon icon="fa-solid fa-gift" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>

          <!-- 위로 버튼 -->
          <button
            @click="router.push('/events/위로')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl md:text-2xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1"
              >
                위로
              </h2>
              <p class="text-xs md:text-sm font-medium text-slate-400">
                병문안 등 위로 상황
              </p>
            </div>
            <div
              class="w-14 h-14 md:w-16 md:h-16 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100"
            >
              <font-awesome-icon icon="fa-solid fa-bandage" class="w-6 h-6 md:w-8 md:h-8" />
            </div>
          </button>
        </section>

        <section class="pt-2">
          <div class="text-xs md:text-sm font-bold text-slate-400 mb-3 px-1">
            최근 대화한 인물 목록
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <button
              v-for="person in peopleData"
              :key="person.id"
              @click="goToChatList(person.id)"
              class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
            >
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 md:w-11 md:h-11 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs md:text-sm shadow-sm"
                >
                  {{ person.name[0] }}
                </div>
                <div>
                  <h3
                    class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm md:text-base"
                  >
                    {{ person.name }}
                  </h3>
                  <p class="text-[11px] md:text-xs text-slate-400 mt-0.5">
                    참여 대화방 {{ person.chatRooms.length }}개
                  </p>
                </div>
              </div>
              <div
                class="text-slate-300 group-hover:text-indigo-500 transition-colors"
              >
                <font-awesome-icon
                  icon="fa-solid fa-chevron-right"
                  class="w-4 h-4"
                />
              </div>
            </button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { peopleData } from '../data/mockData';

const router = useRouter();

const goToChatList = (personId) => {
  router.push({
    name: 'chat-list',
    params: { personId },
  });
};
</script>

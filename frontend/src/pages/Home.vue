<template>
  <div class="flex justify-center bg-gray-50 min-h-screen">
    <div
      class="w-full max-w-md bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/30 via-white to-white flex flex-col px-6 pt-12 pb-6 min-h-screen relative select-none"
    >
      <div v-if="!selectedPerson" class="flex flex-col h-full space-y-6">
        <header>
          <h1
            class="text-2xl font-extrabold text-slate-900 tracking-tight mb-2"
          >
            어떤 상황인가요?
          </h1>
          <p class="text-sm font-medium text-slate-500/90">
            적정 축의금/부의금을 확인해보세요.
          </p>
        </header>

        <section>
          <div
            class="flex items-center bg-white rounded-full px-4 py-3 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative group transition-all duration-300 focus-within:shadow-[0_8px_30px_rgb(99,102,241,0.08)]"
          >
            <div
              class="w-9 h-9 bg-gradient-to-tr from-indigo-600 to-violet-500 rounded-full flex items-center justify-center text-white shadow-md shadow-indigo-200"
            >
              <font-awesome-icon icon="fa-solid fa-wand-magic-sparkles" class="w-4 h-4" />
            </div>
            <input
              type="text"
              placeholder="AI에게 바로 물어보기..."
              class="flex-1 bg-transparent border-none outline-none pl-3 text-sm font-medium text-slate-700 placeholder-slate-300"
            />
            <button
              class="text-indigo-500 hover:text-indigo-600 active:scale-90 transition-transform p-1"
            >
              <font-awesome-icon icon="fa-solid fa-paper-plane" class="w-5 h-5 rotate-45" />
            </button>
          </div>
        </section>

        <section class="space-y-4">
          <button
            @click="router.push('/events/축하')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-indigo-100 hover:shadow-[0_12px_35px_rgb(99,102,241,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors mb-1"
              >
                축하
              </h2>
              <p class="text-xs font-medium text-slate-400">
                결혼, 승진, 출산 등
              </p>
            </div>
            <div
              class="w-14 h-14 bg-indigo-50/70 rounded-2xl flex items-center justify-center text-indigo-500 transition-colors group-hover:bg-indigo-100"
            >
              <font-awesome-icon icon="fa-solid fa-heart" class="w-6 h-6" />
            </div>
          </button>

          <button
            @click="router.push('/events/위로')"
            class="w-full flex items-center justify-between p-6 bg-white rounded-3xl shadow-[0_10px_30px_rgb(0,0,0,0.02)] border border-slate-50 hover:border-slate-300 hover:shadow-[0_12px_35px_rgb(148,163,184,0.05)] active:scale-[0.99] transition-all text-left group"
          >
            <div>
              <h2
                class="text-xl font-bold text-slate-800 group-hover:text-slate-900 transition-colors mb-1"
              >
                위로
              </h2>
              <p class="text-xs font-medium text-slate-400">
                병문안 등 위로 상황
              </p>
            </div>
            <div
              class="w-14 h-14 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 transition-colors group-hover:bg-slate-100 group-hover:text-slate-600"
            >
              <font-awesome-icon icon="fa-solid fa-plus" class="w-6 h-6" />
            </div>
          </button>
        </section>

        <section class="pt-2">
          <div class="text-xs font-bold text-slate-400 mb-3 px-1">
            최근 대화한 인물 목록
          </div>
          <div class="space-y-3">
            <button
              v-for="person in peopleData"
              :key="person.id"
              @click="selectedPerson = person"
              class="w-full flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left group"
            >
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center text-white font-bold text-xs shadow-sm"
                >
                  {{ person.name[0] }}
                </div>
                <div>
                  <h3
                    class="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors text-sm"
                  >
                    {{ person.name }}
                  </h3>
                  <p class="text-[11px] text-slate-400 mt-0.5">
                    참여 대화방 {{ person.chatRooms.length }}개
                  </p>
                </div>
              </div>
              <div
                class="text-slate-300 group-hover:text-indigo-500 transition-colors"
              >
                <font-awesome-icon icon="fa-solid fa-chevron-right" class="w-4 h-4" />
              </div>
            </button>
          </div>
        </section>
      </div>

      <div v-else class="flex flex-col h-full space-y-4">
        <header class="flex items-center py-2 border-b border-slate-100">
          <button
            @click="selectedPerson = null"
            class="mr-3 text-slate-600 hover:text-slate-900 active:scale-95 transition bg-white w-8 h-8 rounded-full flex items-center justify-center shadow-sm border border-slate-100"
          >
            <font-awesome-icon icon="fa-solid fa-chevron-left" class="w-4 h-4" />
          </button>
          <h1 class="text-xl font-extrabold text-slate-950">
            {{ selectedPerson.name }}님 관련 대화방
          </h1>
        </header>

        <div
          v-if="selectedPerson.chatRooms.length === 0"
          class="flex flex-col items-center justify-center h-64 text-slate-400"
        >
          <p class="text-sm font-medium">진행 중인 대화방이 없습니다.</p>
        </div>

        <div v-else class="space-y-3 pt-2">
          <button
            v-for="room in selectedPerson.chatRooms"
            :key="room.roomId"
            @click="enterChatRoom(room.roomId)"
            class="w-full flex items-center justify-between p-5 bg-white rounded-2xl border border-slate-100 shadow-[0_8px_25px_rgb(0,0,0,0.01)] hover:border-indigo-100 active:scale-[0.99] transition-all text-left"
          >
            <div class="flex-1 min-w-0 pr-4">
              <div class="flex items-center justify-between mb-2">
                <span
                  class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-600"
                >
                  {{ room.type }}
                </span>
                <span class="text-[11px] text-slate-400 font-medium">{{
                  room.lastTime
                }}</span>
              </div>
              <h4 class="font-bold text-slate-800 text-sm truncate mb-0.5">
                {{ room.title }}
              </h4>
              <p class="text-xs text-slate-500 truncate font-medium">
                {{ room.lastMessage }}
              </p>
            </div>
            <div class="text-slate-300">
              <font-awesome-icon icon="fa-solid fa-comment-dots" class="w-5 h-5" />
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 현재 홈에서 선택된 인물의 상태값 관리 (null이면 홈메인, 선택 시 대화방 리스트)
const selectedPerson = ref(null);

// 인물 리스트 및 인물 내부 대화방 가상 데이터
const peopleData = ref([
  {
    id: 1,
    name: '김철수',
    chatRooms: [
      {
        roomId: 101,
        type: '축하',
        title: '철수형 결혼 축의금 의논방',
        lastMessage: '축의금 10만원 정도가 적당할까?',
        lastTime: '방금 전',
      },
      {
        roomId: 102,
        type: '축하',
        title: '김철수 과장 승진 축하 모임',
        lastMessage: '선물 어떤 거 준비하시나요?',
        lastTime: '어제',
      },
    ],
  },
  {
    id: 2,
    name: '이영희',
    chatRooms: [
      {
        roomId: 201,
        type: '위로',
        title: '영희 부친상 조문방',
        lastMessage: '부의금 봉투 작성하는 법 물어볼게',
        lastTime: '3일 전',
      },
    ],
  },
  {
    id: 3,
    name: '박민수',
    chatRooms: [], // 대화방이 아직 없는 인물 예시
  },
]);

// 특정 대화방 클릭 시 실행될 함수
const enterChatRoom = (roomId) => {
  alert(`대화방 ID: ${roomId} 로 진입합니다.`);
};
</script>

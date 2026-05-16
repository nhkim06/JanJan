export const peopleData = [
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
        history: [
          { sender: 'user', text: '철수형 결혼 축의금 얼마나 하면 좋을까?' },
          { sender: 'ai', text: '보통 친한 사이라면 10만원에서 15만원 정도를 추천해요. 식장에 직접 가시나요?' },
          { sender: 'user', text: '응 직접 가서 밥도 먹을거야.' },
          { sender: 'ai', text: '그렇다면 10만원 이상이 적당하겠네요! 최근 식대 상승을 고려하면 10만원이 가장 무난한 선택입니다.' }
        ]
      },
      {
        roomId: 102,
        type: '축하',
        title: '김철수 과장 승진 축하 모임',
        lastMessage: '선물 어떤 거 준비하시나요?',
        lastTime: '어제',
        history: [
          { sender: 'user', text: '철수 과장님 승진 선물로 뭐가 좋을까?' },
          { sender: 'ai', text: '부담스럽지 않은 선에서 넥타이나 고급 만년필, 혹은 영양제 세트 등을 추천드려요.' }
        ]
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
        history: [
          { sender: 'user', text: '부의금 봉투는 어떻게 써야 해?' },
          { sender: 'ai', text: '봉투 앞면 중앙에는 賻儀(부의)라고 쓰고, 뒷면 왼쪽 아래에 성함을 세로로 적으시면 됩니다.' }
        ]
      },
    ],
  },
  {
    id: 3,
    name: '박민수',
    chatRooms: [],
  },
];

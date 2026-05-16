import { createApp } from 'vue';
import { createPinia } from 'pinia';

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core';

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

/* import specific icons */
import {
  faUserSecret,
  faHouse,
  faRightToBracket,
  faComment,
  faFileLines,
  faGear,
  faHeart,
  faCircleExclamation,
  faFaceSmile,
  faChartLine,
  faUser,
  faEllipsis,
  faChevronLeft,
  faCircleCheck,
  faTriangleExclamation,
  faGift,
  faWandMagicSparkles,
  faBaby,
  faRing,
  faBriefcase,
  faGraduationCap,
  faStore,
  faCakeCandles,
  faRibbon,
  faBriefcaseMedical,
  faPaperPlane,
  faPlus,
  faChevronRight,
  faCommentDots,
  faBandage,
  faComments,
  faChevronDown,
  faXmark,
  faCheck,
} from '@fortawesome/free-solid-svg-icons';

/* add icons to the library */
library.add(
  faUserSecret,
  faHouse,
  faRightToBracket,
  faComment,
  faFileLines,
  faGear,
  faHeart,
  faCircleExclamation,
  faFaceSmile,
  faChartLine,
  faUser,
  faEllipsis,
  faChevronLeft,
  faCircleCheck,
  faTriangleExclamation,
  faGift,
  faWandMagicSparkles,
  faBaby,
  faRing,
  faBriefcase,
  faGraduationCap,
  faStore,
  faCakeCandles,
  faRibbon,
  faBriefcaseMedical,
  faPaperPlane,
  faPlus,
  faChevronRight,
  faCommentDots,
  faBandage,
  faComments,
  faChevronDown,
  faXmark,
  faCheck,
);

import App from './App.vue';
import router from './router';

const app = createApp(App);

app.component('font-awesome-icon', FontAwesomeIcon);

app.use(createPinia());
app.use(router);

app.mount('#app');

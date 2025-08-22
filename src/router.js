import { createRouter, createWebHistory } from 'vue-router';
import AdvancedSearch from './components/AdvancedSearch.vue';
import ConferenceStats from './components/ConferenceStats.vue';

const routes = [
  {
    path: '/',
    redirect: '/advanced-search'
  },
  {
    path: '/advanced-search',
    name: 'advanced-search',
    component: AdvancedSearch
  },
  {
    path: '/stats',
    name: 'stats',
    component: ConferenceStats
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;

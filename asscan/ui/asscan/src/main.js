import '@/assets/css/tailwind.css'
import Vue from 'vue'
import App from './App.vue'
import Vuex from 'vuex'
import VueRouter from 'vue-router'
import HostDetailsList from './components/HostDetailsList'
import Scanner from './components/Scanner'
import store from './store'
Vue.config.productionTip = false

Vue.use(Vuex)

const routes = [
  { path: '/scanner', name: 'scanner', component: Scanner },
  { path: '/results/:ip', name: 'results', component: HostDetailsList },
]
const router = new VueRouter({
  routes
})

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')

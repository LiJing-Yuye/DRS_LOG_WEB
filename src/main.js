import Vue from 'vue'
import App from './App.vue'
import './plugins/element.js'

Vue.config.productionTip = false

import axios from 'axios'
axios.defaults.timeout = 6000000
Vue.prototype.$http = axios.create({
    baseURL: '/api',
})

new Vue({
    render: (h) => h(App),
}).$mount('#app')

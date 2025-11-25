import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UploadFile from '@/components/UploadFile.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: UploadFile   //Podemos poner tanto una view como un component
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

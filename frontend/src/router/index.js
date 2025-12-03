import { createRouter, createWebHashHistory } from 'vue-router'
import UploadFile from '@/components/UploadFile.vue'
import UserProfile from '@/views/UserProfile.vue'
import QueryList from '../views/QueryList.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: UploadFile   //Podemos poner tanto una view como un component
  },
  {
    path: '/usersList',
    name: 'UserList',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import('../views/UserList.vue')
    }
  },
  {
    path: '/queryList',
    name: 'QueryList',
    component: function () {
      return import('../views/QueryList.vue')
    }
  }, 
  {
    // Esto no tiene nada que ver con el endpoint de la api, es la url que se muestra en el navegador, por eso sigue otro formato distinto al de /api/logs/ NO CONFUNDIR
    path: '/users/:username',
    name: 'UserProfile',
    component: () => import('@/views/UserProfile.vue')
  },
  {
    path: '/users/:username',
    name: 'UserGraphics',
    component: () => import('@/views/UserGraphics.vue')
  },

]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

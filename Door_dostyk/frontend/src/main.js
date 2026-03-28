import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import OrdersView from "./views/OrdersView.vue";
import ShipmentsView from "./views/ShipmentsView.vue";

const routes = [
  { path: "/", redirect: "/orders" },
  { path: "/orders", component: OrdersView },
  { path: "/shipments", component: ShipmentsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");

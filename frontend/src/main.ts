import routes from "./routes";

import { createHead } from "@vueuse/head";
import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";

const app = createApp(App);
const pinia = createPinia();
const head = createHead();

import "./index.css";

import "@iconify/iconify";
import "@purge-icons/generated";

app.use(routes);
app.use(pinia);
app.use(head);

app.mount("#app");

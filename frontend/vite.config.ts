import VueI18n from "@intlify/vite-plugin-vue-i18n";
import Vue from "@vitejs/plugin-vue";
import path from "path";
import AutoImport from "unplugin-auto-import/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import { defineConfig, loadEnv } from "vite";
import PurgeIcons from "vite-plugin-purge-icons";

export default ({ mode }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };

  return defineConfig({
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
        "vue-i18n": "vue-i18n/dist/vue-i18n.cjs.js",
      },
    },
    plugins: [
      Vue(),

      Components({
        dts: true,
        deep: true,
        directoryAsNamespace: true,
        include: [/\.vue$/, /\.vue\?vue/],
        globalNamespaces: ["views", "components", "pages"],
        dirs: ["src/views", "src/components", "src/layouts", "src/pages"],
        resolvers: [
          IconsResolver({
            componentPrefix: "icon",
          }),
        ],
      }),

      AutoImport({
        include: [/\.[tj]sx?$/, /\.vue$/, /\.vue\?vue/, /\.md$/],
        imports: [
          "@vueuse/core",
          "@vueuse/head",
          "pinia",
          "vue",
          "vue-i18n",
          "vue-router",
        ],
        eslintrc: {
          enabled: true,
        },
      }),

      Icons(),
      PurgeIcons(),

      VueI18n({
        runtimeOnly: true,
        compositionOnly: true,
        include: [path.resolve(__dirname, "i18n/**")],
      }),
    ],

    server: {
      fs: {
        strict: true,
      },
    },

    optimizeDeps: {
      include: ["vue", "vue-router", "@vueuse/core"],
    },
  });
};

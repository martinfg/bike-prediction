<script setup lang="ts"></script>

<template>
  <div class="flex flex-col h-full">
    <slot name="header"></slot>

    <main class="container flex-grow px-8 py-12 mx-auto">
      <slot name="content"></slot>
    </main>

    <slot name="footer"></slot>
  </div>
</template>

<style></style>

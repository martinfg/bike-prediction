<script setup lang="ts"></script>

<template>
  <nav class="bg-base-300">
    <div class="container mx-auto navbar">
      <div class="navbar-start">
        <span class="btn btn-ghost normal-case text-xl">Spam Detector</span>
      </div>

      <div class="navbar-end">
        <ul class="menu menu-horizontal p-0 space-x-4">
          <li>
            <router-link :to="{ name: 'Home' }">
              <icon-mdi-home></icon-mdi-home>
              Home
            </router-link>
          </li>

          <li>
            <router-link :to="{ name: 'Classifier' }">
              <icon-mdi-traffic-light></icon-mdi-traffic-light>
              Classifier
            </router-link>
          </li>

          <li>
            <router-link :to="{ name: 'About' }"> About </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style></style>

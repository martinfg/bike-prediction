<script setup lang="ts">
import ky, { HTTPError, Options, TimeoutError } from "ky";

const predictions = [
  {
    date: "morgen",
    confidence: 80,
    weather: {
      degree: 24,
      sky: "sonnig",
    },
    regions: [
      {
        name: "Leipzig Nord",
        availableBikes: 5,
      },
      {
        name: "Leipzig Mitte",
        availableBikes: 10,
      },
      {
        name: "Leipzig Süd",
        availableBikes: 2,
      },
    ],
  },
];

const getColor = (confidence: number) => {
  if (confidence <= 30) {
    return "red";
  } else if (confidence <= 70) {
    return "orange";
  } else {
    return "green";
  }
};

const getPredictions = () => {
  const url = `${import.frontend.env.FAST_API_URL}`;

  try {
    const response = ky.get(url);
  } catch (error) {
    console.log(error);
  }
};
</script>

<template>
  <div
    class="bg-emerald-500 w-screen h-screen flex items-center justify-center"
  >
    <div
      v-for="(prediction, index) in predictions"
      :key="index"
      class="border-3 rounded-3xl p-6 bg-gray-800"
    >
      <div class="inline-flex justify-between w-100">
        <h1 class="font-semibold text-2xl">
          Vorhersage für {{ prediction.date }}
        </h1>
      </div>

      <div class="text-sm font-semibold flex justify-between mt-2">
        <div
          :style="{
            color: getColor(prediction.confidence),
          }"
        >
          {{ prediction.confidence }}% Wahrscheinlichkeit
        </div>
      </div>

      <div
        v-for="(region, index) in prediction.regions"
        :key="index"
        class="mt-6"
      >
        <h2 class="font-semibold text-xl mb-2">
          {{ region.name }}
        </h2>

        <div class="flex text-xl">
          {{ region.availableBikes }}
          <icon-mdi-bicycle class="ml-2" />
        </div>

        <div class="border-1 my-8"></div>
      </div>
    </div>
  </div>
</template>

<style lang="postcss"></style>

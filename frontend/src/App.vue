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

const getWeatherData = async () => {
  const apiKey = "4cbe3a88b8d9c0b2e2df389a51f37303";

  const url = `https://api.openweathermap.org/data/2.5/weather?q=Leipzig&appid=${apiKey}`;

  const json = await ky.get(url).json();
  console.log(json);
};

const getColor = (confidence: number) => {
  if (confidence <= 30) {
    return "red";
  } else if (confidence <= 70) {
    return "orange";
  } else {
    return "green";
  }
};

onMounted(async () => {
  await getWeatherData();
});
</script>

<template>
  <div class="bg-emerald-500 w-screen h-screen flex items-center justify-center">
    <div v-for="(prediction, index) in predictions" :key="index" class="border-3 rounded-3xl p-6 bg-white">
      <div class="inline-flex justify-between w-100">
        <h1 class="font-semibold text-2xl">
          Vorhersage für {{ prediction.date }}
        </h1>

        <div class="flex text-2xl">
          <div class="mr-2 font-semibold">{{ prediction.weather.degree }}°</div>

          <div v-if="prediction.weather.sky === 'sonnig'">
            <icon-mdi-weather-sunny class="text-2xl" />
          </div>

          <div v-else-if="prediction.weather.sky === 'bewölkt'">
            <icon-mdi-cloud class="text-2xl" />
          </div>

          <div v-else-if="prediction.weather.sky === 'regnerisch'">
            <icon-mdi-weather-pouring class="text-2xl" />
          </div>
        </div>
      </div>

      <div class="text-sm font-semibold flex justify-between mt-2">
        <div :style="{
          color: getColor(prediction.confidence),
        }">
          {{ prediction.confidence }}% Wahrscheinlichkeit
        </div>

        <div>Möchtest du ein Fahhrad buchen?</div>
      </div>

      <div v-for="(region, index) in prediction.regions" :key="index" class="mt-6">
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

<style lang="postcss">
</style>

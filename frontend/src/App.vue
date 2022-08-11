<script setup lang="ts">
import ky from "ky";

interface Prediction {
  index: number;
  predicting_from: number;
  predicting_for: number;
  hours_ahead: number;
  grid_id: string;
  free_bikes: number;
}

interface Region {
  name: string;
  id: string;
}

const predictions = ref<Prediction[]>([]);

const availableRegions = [
  {
    name: "Augustusplatz",
    id: "881f1a8cb7fffff",
  },
  {
    name: "Clara-Park",
    id: "881f1a8ca7fffff",
  },
  {
    name: "Lene-Voigt-Park",
    id: "881f1a1659fffff",
  },
];

const selectedRegionId = ref<Region>();

const getRegionName = (prediction: Prediction) => {
  return availableRegions.find((region) => region.id === prediction.grid_id)
    ?.name;
};

const getDate = () => {
  const date = new Date(Date.now());
  return date.toLocaleDateString();
};
const getPredictions = async () => {
  if (selectedRegionId.value) {
    const url = `${import.meta.env.VITE_BACKEND_URL}/pvprediction/${
      selectedRegionId.value
    }/`;
    // const url = `https://t8.se4ai.sws.informatik.uni-leipzig.de/fastapi/pvprediction/${selectedRegionId.value}/`;

    console.log(url);
    try {
      predictions.value = await ky.get(url).json();

      console.log(predictions.value);
    } catch (error) {
      console.log(error);
    }
  }
};

watch(() => selectedRegionId.value, getPredictions);

onMounted(() => {
  getPredictions();
});
</script>

<template>
  <div
    class="bg-emerald-500 w-screen h-screen flex items-center justify-center"
  >
    <div class="border-3 rounded-3xl py-6 px-8 bg-gray-800 text-white">
      <h1 class="font-semibold text-2xl mb-4">
        Fahrad-Verfügbarkeit Vorhersage für den
        {{ getDate() }}
      </h1>

      <div class="flex justify-center">
        <div class="mr-2">Wähle einen Ort aus:</div>
        <select v-model="selectedRegionId" class="text-black">
          <option
            v-for="(region, index) in availableRegions"
            :key="index"
            :value="region.id"
          >
            {{ region.name }}
          </option>
        </select>
      </div>

      <div v-if="predictions.length > 0">
        <div class="mt-6">
          <h2 class="font-semibold text-xl mb-2">
            {{ getRegionName(predictions[0]) }}
          </h2>

          <div
            class="flex text-xl mb-6"
            v-for="(prediction, index) in predictions"
            :key="index"
          >
            <div class="mr-4">
              <div v-if="prediction.hours_ahead === 1">
                In {{ prediction.hours_ahead }} Stunde:
              </div>
              <div v-else>In {{ prediction.hours_ahead }} Stunden:</div>
            </div>

            <div class="flex">
              {{ prediction.free_bikes }}
              <icon-mdi-bicycle class="ml-2" />
            </div>
          </div>

          <div class="border-1 my-8"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="postcss"></style>

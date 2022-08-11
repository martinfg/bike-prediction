<script setup lang="ts">
import { ClassifierService } from "../services/classifier/ClassifierService";

const router = useRouter();

const data = reactive({
  text: "",
});

const feedback = reactive({
  label: 0.5,
});

const result = ref();

const classify = async () => {
  result.value = await ClassifierService.classify(data);
};

const sendFeedback = async () => {
  try {
    await ClassifierService.sendFeedback({
      ...data,
      ...feedback,
    });

    router.push({ name: "Feedback" });
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <div class="card bg-neutral text-neutral-content shadow-xl">
      <div class="card-body">
        <h2 class="card-title">Email Spam Detector</h2>

        <div class="form-control">
          <label class="label">
            <span class="label-text">Email content</span>
          </label>
          <textarea
            class="textarea textarea-bordered"
            placeholder="Email content"
            rows="8"
            v-model="data.text"
          ></textarea>
        </div>

        <div class="card-actions justify-end">
          <button @click="classify" class="btn btn-primary">Check</button>
        </div>
      </div>
    </div>

    <div class="card shadow-xl bg-base-300">
      <div class="card-body">
        <h2 class="card-title">Result</h2>

        <template v-if="result">
          <div class="flex-grow">
            <div>{{ result }}</div>
          </div>

          <div class="grid gap-4">
            <div>Don't agree? <b>Send us your feedback!</b></div>

            <label class="grid gap-4">
              <span>
                How likely do you think it is that this email is spam?
              </span>

              <div>
                <input
                  type="range"
                  :min="0"
                  :max="1"
                  class="range"
                  :step="0.25"
                  v-model.number="feedback.label"
                />
                <div class="w-full flex justify-between text-xs px-2">
                  <span>Unlikely</span>
                  <span>Likely</span>
                </div>
              </div>
            </label>

            <div class="card-actions justify-end">
              <button @click="sendFeedback" class="btn btn-primary">
                Send Feedback
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="h-full flex items-center justify-center italic">
            Please insert the email text and click on check...
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style></style>

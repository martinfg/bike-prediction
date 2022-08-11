import ky from "ky";
import { ClassifyEmailDto } from "./dtos/classify-email.dto";
import { SendFeedbackDto } from "./dtos/send-feedback.dto";

export const ClassifierService = {
  classify: async (dto: ClassifyEmailDto) => {
    const url = new URL(
      "api/emails/classify",
      import.meta.env.VITE_BACKEND_URL
    );

    return await ky.post(url, { json: dto }).json();
  },

  sendFeedback: async (dto: SendFeedbackDto) => {
    const url = new URL("api/feedbacks", import.meta.env.VITE_BACKEND_URL);

    return await ky.post(url, { json: dto }).json();
  },
};

import { ActivityHandler, CardFactory } from "botbuilder";
import axios from "axios";
import fs from "fs";
import path from "path";

// Load Adaptive Cards
const inputCard = JSON.parse(
  fs.readFileSync(path.join(process.cwd(), "cards", "inputCard.json"), "utf-8"),
);
const candidateCardTemplate = JSON.parse(
  fs.readFileSync(
    path.join(process.cwd(), "cards", "candidateCard.json"),
    "utf-8",
  ),
);

export class MyBot extends ActivityHandler {
  constructor() {
    super();

    // Handle messages from user
    this.onMessage(async (context, next) => {
      const value = context.activity.value;

      // Case 1: user submitted feedback
      if (value?.feedback && value?.candidateId) {
        try {
          await axios.post("http://localhost:8000/api/v1/feedback", {
            candidateId: value.candidateId,
            feedbackType: value.feedback,
            reason: value.reason || null,
          });
          await context.sendActivity(`Thanks for your feedback! 👍`);
        } catch (err) {
          console.error(err);
          await context.sendActivity("Oops, failed to send feedback.");
        }
        await next();
        return;
      }

      // Case 2: user submitted input card
      if (value?.query) {
        // Prepare payload
        const payload = {
          query: value.query,
          top_k: 5,
          salary_range:
            value.salaryMin && value.salaryMax
              ? { min: Number(value.salaryMin), max: Number(value.salaryMax) }
              : undefined,
          industry: value.industry || undefined,
          location_filter: value.distanceKm
            ? Number(value.distanceKm)
            : undefined,
        };

        try {
          const res = await axios.post(
            "http://localhost:8000/api/v1/search",
            payload,
          );
          const candidates = res.data.results || [];

          if (candidates.length === 0) {
            await context.sendActivity(
              "No candidates found. Try adjusting your filters.",
            );
          } else {
            // Send each candidate as Adaptive Card
            for (const candidate of candidates) {
              const card = JSON.parse(JSON.stringify(candidateCardTemplate));
              // Replace placeholders
              card.body.forEach((b) => {
                b.text = b.text
                  ?.replace("${candidate.name}", candidate.name)
                  .replace("${candidate.role}", candidate.role)
                  .replace(
                    "${candidate.location.city}",
                    candidate.location?.city || "",
                  )
                  .replace(
                    "${candidate.match_score}",
                    candidate.match_score || "N/A",
                  )
                  .replace(
                    "${candidate.explanation}",
                    candidate.explanation || "",
                  )
                  .replace(
                    "${candidate.skills}",
                    candidate.skills?.join(", ") || "",
                  );
              });
              card.actions.forEach((a) => {
                a.data = { ...a.data, candidateId: candidate.id };
              });

              await context.sendActivity({
                attachments: [CardFactory.adaptiveCard(card)],
              });
            }
          }
        } catch (err) {
          console.error(err);
          await context.sendActivity("Search failed. Please try again.");
        }

        // Send input card again for next search
        await context.sendActivity({
          attachments: [CardFactory.adaptiveCard(inputCard)],
        });
        await next();
        return;
      }

      // Case 3: first message or plain text
      if (!value && context.activity.text) {
        await context.sendActivity(
          "Hi! 👋 I'm BOB, your AI Candidate Assistant. Please describe the role you’re hiring for.",
        );
        await context.sendActivity({
          attachments: [CardFactory.adaptiveCard(inputCard)],
        });
      }

      await next();
    });

    // Handle conversation updates (new members)
    this.onMembersAdded(async (context, next) => {
      const membersAdded = context.activity.membersAdded;
      for (const member of membersAdded) {
        if (member.id !== context.activity.recipient.id) {
          await context.sendActivity(
            "Hi! 👋 I'm BOB, your AI Candidate Assistant. Please describe the role you’re hiring for.",
          );
          await context.sendActivity({
            attachments: [CardFactory.adaptiveCard(inputCard)],
          });
        }
      }
      await next();
    });
  }
}

import { test, expect } from "@playwright/test";

test.describe("Candidate Voice Search UI (FINAL FIXED)", () => {
  // --- 1. App loads ---
  test("App loads correctly", async ({ page }) => {
    await page.goto("http://localhost:5173");

    await expect(page.getByText("Candidate Voice Search")).toBeVisible();
    await expect(page.getByText(/Start Recording/i)).toBeVisible();
  });

  // --- 2. Email input appears (MUI Select FIX) ---
  test("Email input appears when email selected", async ({ page }) => {
    await page.goto("http://localhost:5173");

    // Open MUI Select (acts like button)
    await page.getByText(/Slack – Team Channel/i).click();

    // Click email option from dropdown
    await page.getByRole("option", { name: /Email Distribution/i }).click();

    // Assert email input appears
    await expect(page.getByPlaceholder("recipient@example.com")).toBeVisible();
  });

  // --- 3. Recording button clickable ---
  test("Recording button click works", async ({ page }) => {
    await page.goto("http://localhost:5173");

    const button = page.getByRole("button", { name: /start recording/i });
    await expect(button).toBeVisible();

    await button.click();
  });

  // --- 4. Transcription rendering (MOCK FIX) ---
  test("Displays transcription when voice response arrives", async ({
    page,
  }) => {
    await page.goto("http://localhost:5173");

    // Inject fake response directly into React
    await page.evaluate(() => {
      window.__TEST_VOICE_RESPONSE__ = {
        success: true,
        transcription: "Find IT developers",
        results: [],
      };
    });

    // Simulate WaveRecorder calling callback
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("TEST_VOICE_RESPONSE", {
          detail: window.__TEST_VOICE_RESPONSE__,
        }),
      );
    });

    await expect(page.getByText(/Find IT developers/i)).toBeVisible({
      timeout: 10000,
    });
  });

  // --- 5. Candidate rendering (MOCK FIX) ---
  test("Displays candidate cards when results exist (robust)", async ({
    page,
  }) => {
    await page.goto("http://localhost:5173");

    // Inject mock voice response with candidate
    await page.evaluate(() => {
      window.__TEST_VOICE_RESPONSE__ = {
        success: true,
        transcription: "Find welders",
        results: [
          {
            name: "John Doe",
            role_en: "Welder",
            role: "Hitsaaja",
            experience_years: 10,
            match_score: 90,
            salary: 4000,
            location: { city: "Helsinki", postal_code: "00100" },
            skills: ["TIG", "MIG"],
            licenses: [],
            languages: [],
            summary: "Experienced welder",
            industry: "Teollisuus",
            category: "Industry",
          },
        ],
      };
    });

    // Trigger React event
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("TEST_VOICE_RESPONSE", {
          detail: window.__TEST_VOICE_RESPONSE__,
        }),
      );
    });

    // Wait for transcription to render (ensures React state updated)
    await expect(page.getByText(/Find welders/i)).toBeVisible({
      timeout: 10000,
    });

    // Locate the candidate card by name
    const candidateCard = page.locator("div.MuiCard-root", {
      hasText: "John Doe",
    });
    await expect(candidateCard).toBeVisible({ timeout: 10000 });

    // Match role using regex to avoid matching "Summary: Experienced welder"
    await expect(
      candidateCard.getByText(/^Welder\s*\(Hitsaaja\)/i),
    ).toBeVisible();
  });
});

import * as restify from "restify";
import { BotFrameworkAdapter } from "botbuilder";
import { config } from "dotenv";
import { MyBot } from "./bot.js";

config(); // load .env

const adapter = new BotFrameworkAdapter({
  appId: process.env.MICROSOFT_APP_ID,
  appPassword: process.env.MICROSOFT_APP_PASSWORD,
});

const bot = new MyBot();

const server = restify.createServer();
server.use(restify.plugins.bodyParser());

// Async handler with 2 arguments ONLY
server.post("/api/messages", async (req, res) => {
  await adapter.processActivity(req, res, async (context) => {
    await bot.run(context);
  });
});

server.listen(3978, () => {
  console.log(`\nBot listening on port 3978`);
});

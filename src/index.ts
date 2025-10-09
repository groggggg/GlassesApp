import { AppServer, AppSession, ViewType } from '@mentra/sdk';
import { WebSocket, WebSocketServer} from "ws";

const PACKAGE_NAME = process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY = process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');

const wsServer = new WebSocketServer({ port: 443 });

wsServer.on("connection", (socket) => {
  console.log("Python connected to WebSocket");

  socket.on("message", async (msg) => {
    const data = msg.toString();
    console.log("📩 Message from Python:", data);

    // If you have an active Mentra session, show the result
    if (activeSession) {
      await activeSession.layouts.showTextWall(data);
    }
  });
});

let activeSession: AppSession | null = null;

class ExampleMentraOSApp extends AppServer {

  constructor() {
    super({
      packageName: PACKAGE_NAME,
      apiKey: MENTRAOS_API_KEY,
      port: PORT,
    });
  }

  protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void> {
    // Show welcome message
    session.layouts.showTextWall("Example App is ready!");

    // Handle real-time transcription
    // requires microphone permission to be set in the developer console
    session.events.onTranscription((data) => {
      if (data.isFinal) {
        console.log(data.text)
        session.layouts.showTextWall("You said: " + data.text, {
          view: ViewType.MAIN,
          durationMs: 3000
        });

        wsServer.clients.forEach((client) => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(data.text);
          }
        });
      }
    })
  }
}

// Start the server
// DEV CONSOLE URL: https://console.mentra.glass/
// Get your webhook URL from ngrok (or whatever public URL you have)
const app = new ExampleMentraOSApp();

app.start().catch(console.error);
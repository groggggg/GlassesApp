import { AppServer, AppSession, ViewType } from '@mentra/sdk';
import axios from 'axios';

const PACKAGE_NAME = process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY = process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');

// IMPORTANT: set this in Render's env vars to "https://<your-ngrok-url>.ngrok.io/process"
// or for production a hosted URL
const PYTHON_API_URL = process.env.PYTHON_API_URL ?? "http://localhost:8000/process";

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
    session.events.onTranscription(async (data) => {
      if (data.isFinal) {
        try {
          // send to Python editor
          const resp = await axios.post(PYTHON_API_URL, { text: data.text }, { timeout: 5000 });
          const edited = resp.data?.edited_text ?? "error";

          // display edited text
          session.layouts.showTextWall("Edited: " + edited, {
            view: ViewType.MAIN,
            durationMs: 3000
          });

        } catch (err) {
          console.error();
          // fallback: show original text if remote fails
          session.layouts.showTextWall("Error occured. Message: " + data.text, {
            view: ViewType.MAIN,
            durationMs: 3000
          });
        }
      }
    });

    session.events.onGlassesBattery((data) => {
      console.log('Glasses battery:', data);
    });
  }
}

// Start the server
const app = new ExampleMentraOSApp();
app.start().catch(console.error);

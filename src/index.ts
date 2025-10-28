import { AppServer, AppSession, ViewType } from '@mentra/sdk';
import axios from 'axios';

const PACKAGE_NAME =
  process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY =
  process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');
const PYTHON_API_URL =
  process.env.PYTHON_API_URL ?? "http://localhost:8000/process";

class ExampleMentraOSApp extends AppServer {
  private isRecording = false;
  private recordedText = "";

  constructor() {
    super({
      packageName: PACKAGE_NAME,
      apiKey: MENTRAOS_API_KEY,
      port: PORT,
    });
  }

  protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void> {
    session.layouts.showTextWall("Example App is ready!");

    session.events.onTranscription(async (data) => {
      if (!data.isFinal) return; // only act on final transcriptions
      const text = data.text.toLowerCase().trim();
      console.log("Transcribed:", text);

      // --- Handle start/stop logic ---
      if (text.includes("start") && !this.isRecording) {
        this.isRecording = true;
        this.recordedText = "";
        session.layouts.showTextWall("Recording started...", {
          view: ViewType.MAIN,
          durationMs: 2000
        });
        return;
      }

      if (text.includes("stop") && this.isRecording) {
        this.isRecording = false;
        const toSend = this.recordedText.trim();
        this.recordedText = "";

        session.layouts.showTextWall("Processing recording...", {
          view: ViewType.MAIN,
          durationMs: 2000
        });

        try {
          const resp = await axios.post(PYTHON_API_URL, { text: toSend }, { timeout: 10000 });
          const edited = resp.data?.edited_text ?? toSend;

          session.layouts.showTextWall("Edited: " + edited, {
            view: ViewType.MAIN,
            durationMs: 4000
          });
        } catch (err) {
          console.error("Error contacting Python API:", err);
          session.layouts.showTextWall("Error processing text", {
            view: ViewType.MAIN,
            durationMs: 3000
          });
        }

        return;
      }

      // --- If recording, keep appending ---
      if (this.isRecording) {
        this.recordedText += " " + text;
        console.log("Recording:", this.recordedText);
        return;
      }

      // --- Otherwise, normal behavior ---
      try {
        const resp = await axios.post(PYTHON_API_URL, { text: data.text }, { timeout: 5000 });
        const edited = resp.data?.edited_text ?? data.text;

        session.layouts.showTextWall("Edited: " + edited, {
          view: ViewType.MAIN,
          durationMs: 3000
        });
      } catch (err) {
        console.error("Error contacting Python API:", err);
        session.layouts.showTextWall("You said: " + data.text, {
          view: ViewType.MAIN,
          durationMs: 3000
        });
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

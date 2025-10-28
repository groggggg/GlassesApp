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
    session.layouts.showTextWall("Voice App ready!", {
      view: ViewType.MAIN,
      durationMs: 2000,
    });

    session.events.onTranscription(async (data) => {
      if (!data.isFinal) return;
      const text = data.text.trim();
      const lowerText = text.toLowerCase();
      console.log("Transcribed:", text);

      // --- START recording ---
      if (lowerText.includes("start") && !this.isRecording) {
        this.isRecording = true;
        this.recordedText = "";
        session.layouts.showTextWall("Recording started...", {
          view: ViewType.MAIN,
          durationMs: 1500,
        });
        return; // do not send to Python yet
      }

      // --- STOP recording ---
      if (lowerText.includes("stop") && this.isRecording) {
        this.isRecording = false;
        const toSend = this.recordedText.trim();
        this.recordedText = "";

        if (!toSend) {
          session.layouts.showTextWall("No speech recorded.", {
            view: ViewType.MAIN,
            durationMs: 2000,
          });
          return;
        }

        session.layouts.showTextWall("Processing recording...", {
          view: ViewType.MAIN,
          durationMs: 2000,
        });

        try {
          const resp = await axios.post(PYTHON_API_URL, { text: toSend }, { timeout: 15000 });
          const edited = resp.data?.edited_text ?? toSend;

          // Display the final edited text
          session.layouts.showTextWall("Edited: " + edited, {
            view: ViewType.MAIN,
            durationMs: 5000,
          });
        } catch (err) {
          console.error("Error contacting Python API:", err);
          session.layouts.showTextWall("Error processing text.", {
            view: ViewType.MAIN,
            durationMs: 3000,
          });
        }

        return;
      }

      // --- DURING recording: accumulate and update live ---
      if (this.isRecording) {
        this.recordedText += (this.recordedText ? " " : "") + text;

        // Show live recording (optional: shorten if too long)
        const displayText = this.recordedText.length > 100
          ? this.recordedText.slice(-100) + "…"
          : this.recordedText;

        session.layouts.showTextWall("Recording: " + displayText, {
          view: ViewType.MAIN,
          durationMs: 1000, // updates every second
        });

        return; // do not send to Python yet
      }

      // --- Outside recording: do nothing ---
      // ignored
    });

    session.events.onGlassesBattery((data) => {
      console.log("Glasses battery:", data);
    });
  }
}

const app = new ExampleMentraOSApp();
app.start().catch(console.error);

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
      const text = data.text.toLowerCase().trim();
      console.log("Transcribed:", text);

      // ---- START TRIGGER ----
      if (text.includes("start") && !this.isRecording) {
        this.isRecording = true;
        this.recordedText = "";
        session.layouts.showTextWall("Recording started...", {
          view: ViewType.MAIN,
          durationMs: 1500,
        });
        return; // do not process this text further
      }

      // ---- STOP TRIGGER ----
      if (text.includes("stop") && this.isRecording) {
        this.isRecording = false;
        const toSend = this.recordedText.trim();
        this.recordedText = "";

        if (!toSend) {
          session.layouts.showTextWall("No text recorded.", {
            view: ViewType.MAIN,
            durationMs: 2000,
          });
          return;
        }

        session.layouts.showTextWall("Processing full recording...", {
          view: ViewType.MAIN,
          durationMs: 2000,
        });

        try {
          const resp = await axios.post(PYTHON_API_URL, { text: toSend }, { timeout: 15000 });
          const edited = resp.data?.edited_text ?? toSend;

          session.layouts.showTextWall("Edited: " + edited, {
            view: ViewType.MAIN,
            durationMs: 5000,
          });
        } catch (err) {
          console.error("Error sending to Python API:", err);
          session.layouts.showTextWall("Error processing text.", {
            view: ViewType.MAIN,
            durationMs: 3000,
          });
        }

        return;
      }

      // ---- DURING RECORDING ----
      if (this.isRecording) {
        // append with a space and lowercase text
        this.recordedText += (this.recordedText ? " " : "") + text;
        console.log("Recording so far:", this.recordedText);
        return;
      }

      // ---- OUTSIDE RECORDING ----
      // ignore all other speech
      console.log("Ignoring speech outside recording:", text);
    });

    session.events.onGlassesBattery((data) => {
      console.log("Glasses battery:", data);
    });
  }
}

const app = new ExampleMentraOSApp();
app.start().catch(console.error);

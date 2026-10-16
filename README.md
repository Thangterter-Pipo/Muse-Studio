# 🎨 Muse Studio - Creative AI Control Center

**🌐 Language / Ngôn ngữ:** **English** · [Tiếng Việt](./README.vi.md)

An independent, self-hosted web control center and OpenAI-compatible API gateway for Muse AI. Turn personal Muse accounts into a high-performance local AI studio for image generation, video creation, and LLM chat.

---

## 🌟 Key Features

- **🎨 Image Generation (Muse Image):** High-definition Text-to-Image & Image-to-Image generation with flexible aspect ratios (`16:9`, `1:1`, `9:16`, `4:3`, `3:4`).
- **🎬 Video Production (Muse Video):** Smooth AI motion video generation from text prompts or image references.
- **💬 Streaming AI Chat (Muse Spark):** OpenAI-compatible chat completions with real-time SSE streaming.
- **⚡ Hot-Session Fast Path:** Sub-second dispatch through React DOM state injection and persistent Chromium connection pooling.
- **🔑 Multi-API Key Management:** Generate custom API keys to easily connect external AI apps (Cursor, NextChat, Cherry Studio, Dify, OpenWebUI).
- **🚀 1-Click Auto Browser Login:** Automatically launch Chrome/Edge to log in and extract session cookies via CDP without manual inspection.
- **📊 Real-time Quota & Usage:** Accurately track weekly plan quotas and non-expiring additional token balances in both English and Vietnamese.
- **🔒 100% Local & Privacy-First:** All accounts, cookies, and rendered media are stored strictly on your local machine.

---

## 🚀 Quick Start (Windows)

1. Download the latest release zip from GitHub or clone the repository.
2. Double-click **`start.bat`**.
   - It will automatically set up Python dependencies and launch the server.
3. Your browser will automatically open:
   ```
   http://localhost:18610/studio/
   ```

---

## 🔌 Connecting to External AI Tools

Muse Studio provides a fully OpenAI-compatible API endpoint:

- **Base URL:** `http://localhost:18610/v1` (or `http://127.0.0.1:18610/v1`)
- **API Key:** Go to the **API & Access Keys** tab in Muse Studio and click **Create New Key**.
- **Supported Models:**
  - `muse-spark`: Chat, coding assistance, and reasoning.
  - `muse-image`: Image generation.
  - `muse-video`: Video generation.

### Example: NextChat / Cherry Studio / Cursor
- **Provider:** OpenAI / Custom OpenAI
- **Endpoint:** `http://127.0.0.1:18610/v1`
- **Model:** `muse-spark`

---

## 🛠️ Manual Installation (Cross-Platform)

```bash
# Clone the repository
git clone https://github.com/Thangterter-Pipo/Muse-Studio.git
cd Muse-Studio

# Install requirements
pip install -r requirements.txt

# Run server
uvicorn app:app --host 0.0.0.0 --port 18610
```

---

## ☕ Support the Author

If you find Muse Studio helpful, feel free to support the creator via the built-in **Donate** button in the dashboard!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

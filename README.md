# Gemini Line ChatBot
這是一個使用fastapi開發的Line聊天機器人
## 特色
- 上下文記憶：透過 `interaction_id` 實現連貫的對話體驗。
- 採用模組化設計，將不同服務解耦，方便維護與擴充
## 快速開始
建立.env file
LINE_CHANNEL_SECRET=your_Secret
LINE_CHANNEL_ACCESS_TOKEN=your_Token
GEMINI_API_KEY=your_GeminiKey

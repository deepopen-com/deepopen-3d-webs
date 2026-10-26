CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=ZCOOL+XiaoWei&display=swap');

:root {
  --ink: #1a2332;
  --ink-soft: #5a6577;
  --paper: #fffaf6;
  --coral: #ff5c3a;
  --coral-deep: #e03d1c;
  --sun: #ffb020;
  --teal: #0d9488;
  --teal-bright: #14b8a6;
  --sky: #0891b2;
  --rose: #e11d6a;
  --mint: #34d399;
  --line: rgba(26, 35, 50, 0.08);
  --glass: rgba(255, 250, 246, 0.82);
  --shadow: 0 10px 28px rgba(224, 61, 28, 0.10);
  --radius: 20px;
  --font-display: "ZCOOL XiaoWei", "Noto Sans SC", serif;
  --font-ui: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

html, body, .gradio-container {
  font-family: var(--font-ui) !important;
  color: var(--ink) !important;
}

.gradio-container {
  max-width: 1180px !important;
  margin: 0 auto !important;
  padding: 18px 16px 48px !important;
  background:
    radial-gradient(900px 420px at 8% -5%, rgba(255, 176, 32, 0.35) 0%, transparent 55%),
    radial-gradient(800px 380px at 96% 4%, rgba(20, 184, 166, 0.28) 0%, transparent 50%),
    radial-gradient(700px 360px at 50% 110%, rgba(225, 29, 106, 0.16) 0%, transparent 45%),
    linear-gradient(165deg, #fff4e8 0%, #e8fffb 42%, #fff0f5 100%) !important;
  background-attachment: fixed !important;
}

/* 隐藏 Gradio 默认页脚 */
footer, .svelte-1ipelgc, .built-with {
  display: none !important;
}

/* ===== Hero：品牌优先、全幅氛围 ===== */
#hzq-hero {
  position: relative;
  overflow: hidden;
  margin: 0 0 18px 0;
  padding: 36px 28px 32px;
  border-radius: 28px;
  color: #fff;
  background:
    linear-gradient(125deg, #ff6a3d 0%, #ff8f3c 38%, #14b8a6 78%, #0891b2 100%);
  box-shadow: var(--shadow);
  animation: hzq-hero-in 0.7s ease-out both;
}

#hzq-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 18% 30%, rgba(255,255,255,0.28), transparent 42%),
    radial-gradient(circle at 82% 20%, rgba(255,255,255,0.18), transparent 36%),
    repeating-linear-gradient(
      -18deg,
      transparent 0 14px,
      rgba(255,255,255,0.05) 14px 15px
    );
  pointer-events: none;
  animation: hzq-shimmer 8s linear infinite;
}

#hzq-hero .hzq-hero-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 22px;
  flex-wrap: wrap;
}

#hzq-hero .hzq-logo {
  width: 96px;
  height: 96px;
  border-radius: 22px;
  object-fit: cover;
  flex: 0 0 auto;
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.45);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

#hzq-hero .hzq-hero-text {
  position: relative;
  min-width: 220px;
  flex: 1 1 280px;
}

#hzq-hero .hzq-brand {
  position: relative;
  font-family: var(--font-display) !important;
  font-size: clamp(2.4rem, 5vw, 3.4rem);
  font-weight: 400;
  letter-spacing: 0.06em;
  margin: 0 0 10px 0;
  line-height: 1.15;
  text-shadow: 0 2px 0 rgba(0,0,0,0.06);
}

#hzq-hero .hzq-tagline {
  position: relative;
  margin: 0;
  max-width: 36em;
  font-size: 1.05rem;
  font-weight: 500;
  line-height: 1.55;
  opacity: 0.96;
}

#hzq-hero .hzq-chips {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

#hzq-hero .hzq-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.22);
  border: 1px solid rgba(255,255,255,0.35);
  font-size: 0.82rem;
  font-weight: 700;
  backdrop-filter: blur(6px);
}

#hzq-hero .hzq-chip i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  display: inline-block;
}

/* ===== 统计卡片 ===== */
.hzq-card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin: 4px 0 16px 0;
  animation: hzq-rise 0.55s ease-out 0.12s both;
}

@media (max-width: 900px) {
  .hzq-card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 560px) {
  .hzq-card-grid { grid-template-columns: 1fr; }
}

.hzq-card {
  position: relative;
  overflow: hidden;
  background: var(--glass);
  backdrop-filter: blur(10px);
  border-radius: var(--radius);
  padding: 18px 18px 16px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(26, 35, 50, 0.05);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.hzq-card::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 5px;
  background: var(--accent);
}

.hzq-card::after {
  content: "";
  position: absolute;
  right: -20px; top: -20px;
  width: 88px; height: 88px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  pointer-events: none;
}

.hzq-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(26, 35, 50, 0.10);
}

.hzq-card-kicker {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 6px;
}

.hzq-card-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--ink-soft);
}

.hzq-card-value {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 400;
  color: var(--ink);
  margin: 4px 0 6px;
  line-height: 1.15;
}

.hzq-card-sub {
  font-size: 0.84rem;
  color: var(--ink-soft);
  line-height: 1.4;
}

/* ===== 分区标题 ===== */
.hzq-section {
  margin: 8px 0 14px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255,255,255,0.55);
  border: 1px solid var(--line);
}

.hzq-section h3 {
  margin: 0 0 4px 0;
  font-family: var(--font-display);
  font-size: 1.35rem;
  color: var(--ink);
}

.hzq-section p {
  margin: 0;
  color: var(--ink-soft);
  font-size: 0.95rem;
}

.hzq-sys-panel {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 18px;
  margin-top: 10px;
}

@media (max-width: 700px) {
  .hzq-sys-panel { grid-template-columns: 1fr; }
}

.hzq-sys-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 12px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid var(--line);
}

.hzq-sys-dot {
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border-radius: 50%;
  flex: 0 0 auto;
  background: var(--teal);
}

.hzq-sys-item b {
  display: block;
  font-size: 0.8rem;
  color: var(--ink-soft);
  font-weight: 700;
}

.hzq-sys-item span {
  font-size: 0.95rem;
  color: var(--ink);
  word-break: break-all;
}

/* ===== Tab 菜单：彩色区分、加粗、选中放大 ===== */
.tabs > .tab-nav,
.tab-nav {
  gap: 8px !important;
  flex-wrap: wrap !important;
  background: rgba(255,255,255,0.7) !important;
  backdrop-filter: blur(8px);
  border-radius: 18px !important;
  padding: 10px !important;
  border: 1px solid rgba(255,255,255,0.95) !important;
  margin-bottom: 14px !important;
  box-shadow: 0 6px 18px rgba(26,35,50,0.04) !important;
}

.tab-nav button {
  position: relative !important;
  font-family: var(--font-ui) !important;
  font-weight: 800 !important;
  font-size: 0.98rem !important;
  border-radius: 14px !important;
  padding: 11px 16px !important;
  color: var(--ink) !important;
  background: #fff !important;
  border: 2px solid transparent !important;
  transition: transform 0.18s ease, background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease !important;
}

.tab-nav button::before {
  content: "";
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: 1px;
  background: currentColor;
}

.tab-nav button:nth-child(1) { color: #e03d1c !important; border-color: #ffd0c4 !important; }
.tab-nav button:nth-child(2) { color: #0891b2 !important; border-color: #b6ecf5 !important; }
.tab-nav button:nth-child(3) { color: #0d9488 !important; border-color: #b6f3e9 !important; }
.tab-nav button:nth-child(4) { color: #e11d6a !important; border-color: #fbcfe0 !important; }
.tab-nav button:nth-child(5) { color: #c2410c !important; border-color: #fed7aa !important; }

.tab-nav button.selected,
.tab-nav button[aria-selected="true"] {
  font-size: 1.14rem !important;
  font-weight: 900 !important;
  color: #fff !important;
  background: linear-gradient(135deg, var(--coral) 0%, var(--sun) 55%, var(--teal-bright) 100%) !important;
  border-color: transparent !important;
  box-shadow: 0 10px 22px rgba(255, 92, 58, 0.28) !important;
  transform: translateY(-2px) scale(1.02);
}

.tab-nav button.selected::before,
.tab-nav button[aria-selected="true"]::before {
  background: #fff;
}

/* ===== 表单与面板 ===== */
.panel-card,
.gr-form,
.gr-box,
.block {
  border-radius: 18px !important;
}

.panel-card {
  background: rgba(255,255,255,0.88) !important;
  border: 1px solid var(--line) !important;
  padding: 12px !important;
  box-shadow: 0 8px 20px rgba(26,35,50,0.04) !important;
}

label, .label-wrap span {
  font-weight: 700 !important;
  color: var(--ink) !important;
}

textarea, input, select, .gr-input, .gr-text-input textarea {
  border-radius: 12px !important;
  border-color: #e8ddd4 !important;
  background: #fff !important;
}

button.primary, button.secondary, .gr-button {
  border-radius: 14px !important;
  font-weight: 800 !important;
  transition: transform 0.15s ease, filter 0.15s ease !important;
}

button:hover, .gr-button:hover {
  filter: brightness(1.03);
  transform: translateY(-1px);
}

#run-button, #btn-create, #btn-render, #btn-refresh {
  min-height: 46px !important;
  border: none !important;
  color: #fff !important;
  letter-spacing: 0.02em;
}

#run-button {
  background: linear-gradient(135deg, var(--coral), var(--sun)) !important;
  box-shadow: 0 8px 18px rgba(255, 92, 58, 0.28) !important;
}

#btn-create {
  background: linear-gradient(135deg, var(--sky), #2563eb) !important;
  box-shadow: 0 8px 18px rgba(8, 145, 178, 0.24) !important;
}

#btn-render {
  background: linear-gradient(135deg, var(--teal), #059669) !important;
  box-shadow: 0 8px 18px rgba(13, 148, 136, 0.24) !important;
}

#btn-refresh {
  background: linear-gradient(135deg, #fb7185, var(--coral)) !important;
}

/* Markdown / 表格观感 */
.prose, .markdown, .gr-markdown {
  color: var(--ink) !important;
}

.prose table, .markdown table, .gr-markdown table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  overflow: hidden;
  border-radius: 14px;
  background: #fff;
  border: 1px solid var(--line);
}

.prose th, .markdown th, .gr-markdown th {
  background: linear-gradient(90deg, #fff1e8, #e8fffb);
  font-weight: 800;
  padding: 10px 12px !important;
}

.prose td, .markdown td, .gr-markdown td {
  padding: 9px 12px !important;
  border-top: 1px solid var(--line);
}

@keyframes hzq-hero-in {
  from { opacity: 0; transform: translateY(10px) scale(0.985); }
  to { opacity: 1; transform: none; }
}

@keyframes hzq-rise {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: none; }
}

@keyframes hzq-shimmer {
  from { background-position: 0 0, 0 0, 0 0; }
  to { background-position: 0 0, 0 0, 120px 0; }
}
"""

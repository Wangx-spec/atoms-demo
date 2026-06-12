from app.schemas.apps import GeneratedCodePayload


class CodegenService:
    async def generate_app(self, prompt: str) -> GeneratedCodePayload:
        title = prompt.strip()[:48] or "AI Generated App"
        return GeneratedCodePayload(
            html=f"""
<main class="app-shell">
  <section class="hero">
    <p class="eyebrow">Atoms Demo</p>
    <h1>{title}</h1>
    <p>这是根据你的需求生成的应用原型。你可以继续补充需求，让它逐步变完整。</p>
    <button id="primaryAction">运行交互</button>
  </section>
  <section class="panel">
    <h2>功能清单</h2>
    <ul>
      <li>清晰的首屏结构</li>
      <li>可编辑的 HTML/CSS/JS</li>
      <li>iframe sandbox 安全预览</li>
    </ul>
  </section>
</main>
""".strip(),
            css="""
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f7f4ef;
  color: #1b1f23;
}
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
  gap: 24px;
  padding: 32px;
}
.hero, .panel {
  border: 1px solid #d8d3ca;
  background: #fffdfa;
  border-radius: 8px;
  padding: 28px;
}
.eyebrow {
  margin: 0 0 12px;
  color: #396a5f;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}
h1 {
  margin: 0 0 16px;
  font-size: clamp(32px, 6vw, 64px);
  line-height: 1;
}
button {
  margin-top: 18px;
  border: 0;
  border-radius: 6px;
  background: #1f6f8b;
  color: white;
  padding: 12px 16px;
  font-weight: 700;
  cursor: pointer;
}
@media (max-width: 760px) {
  .app-shell { grid-template-columns: 1fr; padding: 18px; }
}
""".strip(),
            js="""
const button = document.querySelector("#primaryAction");
button?.addEventListener("click", () => {
  button.textContent = "交互已触发";
});
""".strip(),
        )


codegen_service = CodegenService()

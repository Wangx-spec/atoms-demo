from app.schemas.apps import GeneratedCodePayload
from app.services.llm_service import LLMError, MockLLMProvider, get_llm_provider

CODEGEN_SYSTEM = (
    "你是一名资深前端工程师。根据用户需求生成一个独立的单页应用。"
    "只返回一个 JSON 对象，包含三个字段：html、css、js。"
    "html 不要包含 <html>/<head>/<body>/<style>/<script> 标签，只写 body 内部结构；"
    "css 写完整样式；js 写交互逻辑（不使用外部依赖）。"
)
CODEGEN_SCHEMA = '{"html": "string", "css": "string", "js": "string"}'


class CodegenService:
    async def generate_app(
        self,
        prompt: str,
        analysis: str | None = None,
        structure: str | None = None,
    ) -> GeneratedCodePayload:
        provider = get_llm_provider()
        if not isinstance(provider, MockLLMProvider):
            try:
                user_prompt = self._build_prompt(prompt, analysis, structure)
                data = await provider.generate_json(
                    user_prompt, schema_hint=CODEGEN_SCHEMA, system=CODEGEN_SYSTEM
                )
                html = (data.get("html") or "").strip()
                if html:
                    return GeneratedCodePayload(
                        html=html,
                        css=(data.get("css") or "").strip(),
                        js=(data.get("js") or "").strip(),
                    )
            except (LLMError, ValueError, KeyError):
                pass  # fall back to the deterministic mock template below
        return self._mock_app(prompt)

    def _build_prompt(self, prompt: str, analysis: str | None, structure: str | None) -> str:
        parts = [f"用户需求：{prompt}"]
        if analysis:
            parts.append(f"需求分析：{analysis}")
        if structure:
            parts.append(f"页面结构规划：{structure}")
        return "\n".join(parts)

    def _mock_app(self, prompt: str) -> GeneratedCodePayload:
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

# 公众号首图卡片模板(HTML 生成)

读取时机:不想用视频缩略图、OG 图或文档截图作封面,而是想生成一张和文章主旨直接对齐的原创卡片。

---

## 设计哲学

一张极简纯白的题图,把"事件 → 事实 → 命题 → 来源"四层信息压在 900×383 一张图里。

四个核心约束:

1. **背景纯白(`#ffffff`)**:不是暖色调、不是浅灰,纯白才让粗黑字立起来。
2. **无衬线 + 700 字重**:中文走 `PingFang SC`,英文走 `Inter` / `SF Pro Display`。字重 700 + 字间距 -1.2px,得到接近"产品沉思录"那种几何感强、笔画厚的现代无衬线效果。**禁止 Georgia / 思源宋体 / 任何衬线主标题**,会立刻偏古典,跟极简感冲突。
3. **黑灰单色为底,可选一处渐变焦点**:全图只有三档黑灰(`#111` 主标题 / `#444` 引语 / `#999` 元信息) + 一根 1px hairline (`#e6e6e6`)。主标题可选用一处水平渐变作焦点(橙紫 / 蓝紫 / 全黑),其他元素一律纯黑灰,不允许第二处彩色。
4. **左右上下四角都有锚点**:左上 kicker、中间主标题、底部 hairline、左下金句、右下出处,留白被结构化使用,不会显得空。

---

## 适用场景

走这种模板的判断标准:

- 文章是技术 / AI / SaaS / 创业类,读者预期"现代科技感"
- 想让封面**和文章主旨直接对齐**(标题就是文章观点,金句就是文章核心命题),而不是用一张演讲现场截图代表
- 公众号在 timeline 里需要靠**文字密度和对比**抢眼,而不是靠图像感染
- 不想引入暖羊皮纸 + Georgia 衬线 + Terracotta 那套"高级编辑手册"风格(见 `claude-design-card` skill)

不适用:

- 文章是文学 / 哲学 / 散文 / 访谈类,需要"温度"和"质感",这种纯白会显得冷硬
- 内容主角是一张已经很有视觉冲击力的现场画面(嘉宾正脸、产品截图、关键图表),用模板反而稀释
- 公众号读者群偏文化向,会觉得这种 marketing 配色"AI 味太重"

---

## 信息架构

每张卡片严格按四层信息组织,**多一层就乱**:

| 层 | 内容性质 | 字号 | 字重 | 颜色 | 位置 |
| --- | --- | --- | --- | --- | --- |
| Kicker | 作者 banner + 期号(如 `大锤沉思录 · 2026.05`) | 12px | 600 | `#999` | 左上 |
| 主标题 | 文章一句话主旨 | 42px | 700 | 黑或渐变 | 中上 |
| Hairline | 一根全宽 1px 灰线,把上下切开 | — | — | `#e6e6e6` | 中部 |
| 金句 | 文章核心命题(原文金句) | 22px | 700 | `#111` | 左下 |
| Meta | 来源说明,如嘉宾 + 节目 | 13px | 500 | `#999`,右对齐 | 右下 |

**金句不带句号、kicker 不带句号**,主标题本身也是不完整句不需句号——所有文案末尾不收标点,极简感的一部分。

主标题超过 14 个汉字时**改写**,不要硬缩字号或换行。一行装不下宁可砍字,不要让标题断成两行后第二行只剩一两个字。

---

## 完整 HTML 模板

把所有 `{{...}}` 字段替换为内容,保存为 `/tmp/cover.html`,然后用本文末的命令截图。

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>{{文章标题}} — 公众号首图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 900px;
    height: 383px;
    background: #ffffff;
    font-family: -apple-system, "PingFang SC", "Inter", "Helvetica Neue", system-ui, sans-serif;
    color: #111111;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
  }
  .card {
    width: 900px;
    height: 383px;
    padding: 50px 72px;
    display: flex;
    flex-direction: column;
  }
  .kicker {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.8px;
    color: #999999;
  }
  .title {
    font-size: 42px;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: -1.2px;
    margin-top: 28px;
    white-space: nowrap;
    /* 渐变三选一,见下方"渐变变体"表 */
    background: linear-gradient(90deg, #E5604D 0%, #D4517A 45%, #B05BB8 75%, #A06CD5 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
  }
  .hairline {
    height: 1px;
    background: #e6e6e6;
    margin-top: 44px;
  }
  .row-bottom {
    margin-top: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .quote {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.4;
    color: #111111;
    letter-spacing: -0.4px;
  }
  .meta {
    font-size: 13px;
    font-weight: 500;
    color: #999999;
    line-height: 1.5;
    text-align: right;
    white-space: nowrap;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="kicker">{{作者公众号名}} · {{年.月,如 2026.05}}</div>
    <h1 class="title">{{主标题,12-14 字内,一句话讲文章主旨}}</h1>
    <div class="hairline"></div>
    <div class="row-bottom">
      <div class="quote">{{文章金句,16 字内,无句号}}</div>
      <div class="meta">{{出处第一行,如 嘉宾名 + 动作}}<br/>{{出处第二行,如 节目名 / 文章定位}}</div>
    </div>
  </div>
</body>
</html>
```

---

## 渐变变体

主标题的 `background` 三选一,根据文章调性挑:

| 变体 | CSS | 调性 |
| --- | --- | --- |
| **橙紫(默认)** | `linear-gradient(90deg, #E5604D 0%, #D4517A 45%, #B05BB8 75%, #A06CD5 100%)` | 当下 AI / SaaS marketing 主流,温暖偏现代 |
| **蓝紫(冷调)** | `linear-gradient(90deg, #4F8FFF 0%, #7B6CF5 50%, #A06CD5 100%)` | 工程 / 技术深度 / 算法类内容,冷感更强 |
| **全黑(无渐变)** | 删掉 `background`/`-webkit-background-clip`/`-webkit-text-fill-color`,改用 `color: #111111` | 严肃议题 / 哲学 / 商业评论,完全克制 |

**只在主标题用渐变,其他元素一律不彩**。如果金句也想加色,先停下问自己"画面里需要两个焦点吗",答案几乎总是不需要。

---

## 截图命令

不依赖 Bun / Playwright,直接用 Chrome / Chromium headless。Chrome 路径按平台:

```bash
# macOS
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Linux(任选一个,看哪个装了)
CHROME="/usr/bin/google-chrome"           # Google Chrome
CHROME="/usr/bin/chromium"                # Chromium
CHROME="/usr/bin/chromium-browser"        # Ubuntu / Debian 旧路径

# Windows(PowerShell / Git Bash)
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
```

确认路径后跑命令:

```bash
"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 \
  --window-size=900,383 \
  --screenshot=cover.png \
  file:///tmp/cover.html
```

输出 `cover.png` 是 1800×766 的 2x DPR 高清图。如果要用作微信公众号首图(`.jpg`),把 PNG 转 JPG:

```bash
# macOS 自带
sips -s format jpeg cover.png --out cover.jpg

# Linux / Windows 用 ImageMagick(需安装)
convert cover.png cover.jpg
# 或者用 ffmpeg
ffmpeg -i cover.png -y cover.jpg
```

**环境检查**:命令报"command not found"或"无法识别"时,先用 `which google-chrome` / `which chromium` / `where chrome.exe` 确认实际路径。所有现代 Chromium-based 浏览器(Edge、Brave、Vivaldi)都支持 `--headless` 模式,可以替换。

如果需要边迭代边看效果(比如调字号、调渐变),更顺手的做法是用 Chrome DevTools MCP 打开 `file:///tmp/cover.html`、`resize_page` 到 900×383、然后 `take_screenshot`,改完直接 reload 即可。最终定稿出 PNG 还是用上面的 headless 命令,得到稳定的 2x 高清图。

---

## 字段填法

### Kicker

格式固定 `{{作者公众号名}} · {{年.月}}`,中点之间各空一格。"年.月"用阿拉伯数字 + 点(如 `2026.05`),不用"5 月"或斜杠日期。

### 主标题

12-14 个汉字内最佳,一行能装下。这是个硬约束:超过 14 个字会硬缩字号或换行,两种结果都丑。

写主标题的两个原则:
- **是结论,不是主题名**。"YC 把自己改成了一家 AI 原生公司" ✓ / "YC 内部 AI 实践" ✗
- **优先用动词**。"把自己改成了"、"砍掉"、"放弃了"、"重写了"比"关于"、"浅谈"、"...的思考" 强很多

### 金句

来自原文,严禁捏造。两个要求:
- 16 个汉字以内,一行装下
- 无句号(末尾自然断,极简感的一部分)

挑金句的优先级:
1. 文章里**最反直觉**的判断
2. 文章里**最具体**的方法论一句话
3. 作者主推荐(transcript.md 里挑出来的金句库)

### Meta

两行,右对齐:
- 第一行:嘉宾名 + 一个动词(如 `Pete Koomen 第一次公开`)
- 第二行:出处 / 文章定位(如 `YC 的内部 playbook`)

如果是网页文章 / PDF 改写,第一行写作者名,第二行写媒体名或文章性质。如果完全是原创观点(没有嘉宾),meta 可以只一行,或者改成"大锤沉思录 · 原创"。

---

## 字号微调表(标题文字超长时)

模板默认主标题 42px,适合 12-14 字。超出时按下表降字号 + 收紧字间距。**永远不要让标题换行**:

| 主标题字数 | font-size | letter-spacing |
| --- | ---: | ---: |
| ≤ 12 字 | 46-48px | -1.0px |
| 13-14 字 | 42px(默认) | -1.2px |
| 15-16 字 | 38px | -1.4px |
| 17 字以上 | 重写,不要降字号 | — |

`white-space: nowrap` 已经强制不换行,所以超出时画面会被截掉——**这是设计性 fail-loud**,提醒你回去改标题,不要靠缩字号挽救。

---

## 反模式

不要做的事:

- 在主标题之外加第二处彩色(金句、kicker、meta)。整图只有一处焦点。
- 用衬线字体做主标题(Georgia / 思源宋体 / 思源思宋)。这套模板的极简感建立在"无衬线 + 厚字重"上,衬线立刻倒退到 `claude-design-card` 那套暖底质感。
- 在 hairline 之外加任何装饰(图标、符号、SVG 装饰、引号、虚线)。
- 把整篇文章的章节列在封面上。封面不是目录,是钩子。
- 用斜体强调中文。中文斜体在浏览器里是机械倾斜,很丑。
- padding 改成 < 40px。留白被吃掉之后,极简感就没了。
- 主标题字数超过 17 个还要塞进去。回去改文案。

---

## 与 `claude-design-card` skill 的关系

这是一种**和 claude-design-card 并行的封面风格**,不是替代关系。两者的取舍:

| 维度 | 本模板(极简纯白) | `claude-design-card` |
| --- | --- | --- |
| 背景 | 纯白 `#ffffff` | 暖羊皮纸 `#f5f4ed` |
| 主字体 | PingFang SC / Inter,无衬线 700 | Georgia / 思源宋体,衬线 500 |
| 强调色 | 可选渐变(橙紫 / 蓝紫) | Terracotta `#c96442` 单色 |
| 信息密度 | 4 层(kicker / 标题 / 金句 / meta) | 3 层(kicker / 标题 / 一个证据点) |
| 适合内容 | AI / 技术 / SaaS / 现代议题 | 文学 / 哲学 / 编辑深度 / 文化评论 |
| 出图工具 | Chrome headless,零依赖 | Bun + Playwright(需安装) |
| 出图风格 | "Stripe / Linear / Notion" 现代极简 | "纽约客 / 编辑手册" 经典印刷 |

写稿时,如果文章风格不确定,**默认用本模板**(极简纯白),因为它出图门槛低、读者覆盖更广。只有文章本身就是文学 / 哲学 / 文化评论时,才换 `claude-design-card`。

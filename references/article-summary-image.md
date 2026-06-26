# 文章顶部摘要图(HTML 渲染 + 截图)

读取时机:文章主题适合用一张图把全文结构在一屏内呈现时。典型触发场景:讲方法论 / 工作流 / 分层结构 / 多阶段进阶,且这些结构本身就是文章的核心论点。

> **⚠️ 生成时机：必须等用户确认定稿后再生成。**
> 摘要图的标题和文案来自文章标题和正文结构。用户通常会在初稿后多轮修改内容，若在初稿阶段就生成图，终稿改完后图与文章会不一致。
> **正确流程**：写完 `article.md` → 用户审阅、逐段精修、确认内容 → 用户通知"可以生成图了" → 再生成 summary.html + 截图。
> 封面图（cover.jpg）同理，也在定稿后生成。

---

## 一、为什么用 HTML + 截图,而不是 Figma / PPT / 在线生成器

这套做法是 **本 skill 的「实操即论证」动作**。当文章本身在讲"AI 时代的输出格式应该更密、更人眼友好"(参考 Thariq Shihipar 的「The Unreasonable Effectiveness of HTML」)时,顶图本身就应该是一份 HTML spec——形式即内容。

具体优势:

- **可二次编辑**:HTML 源码留在仓库,以后改文案、改字体、改字号都是文本编辑
- **字体精准**:Google Fonts / 自托管字体,所见即所得,不依赖 Figma 的字体安装
- **信息密度可控**:Grid + Flex 排版让"刚好够呼吸"的留白容易调
- **截图清晰**:macOS Retina 屏 + Chrome DevTools `take_screenshot` 自动 2x scale,文字不糊
- **文件小**:纯白底 + 极简内容的截图大约 200KB,远小于密集 1MB+ 的设计

如果文章主题不需要"形式即内容"(比如纯叙事型、纯访谈、纯新闻报道),可以跳过这条流程,直接用视频封面或截图做顶图。

---

## 二、工具链

```
frontend-design skill  →  写 HTML+CSS  →  Chrome DevTools MCP 打开  →  take_screenshot  →  嵌入 article.md
```

具体步骤:

1. 调用 `/frontend-design` skill 获取设计原则,**不要**直接套用过往设计——每次刻意换字体方案、配色思路,避免 AI 生成稿的"千篇一律"
2. 在 `article.md` 同目录写 `<日期>-<videoid>-summary.html`
3. `mcp__chrome-devtools__resize_page` 设置 viewport(下面讲尺寸)
4. `mcp__chrome-devtools__new_page` 或 `navigate_page` 打开本地 file:// URL
5. `sleep 2` 等 Web Fonts 加载完成(不等会 fallback 到系统字体,样式会偏)
6. `mcp__chrome-devtools__take_screenshot` 用 `fullPage: true` 截图为 PNG
7. 在 `article.md` 主标题之后用 `![alt](path)` 嵌入

---

## 三、画布尺寸 + 信息密度

**默认假设:大部分用户在手机上读公众号**。这一条决定后面所有取舍。

### 推荐尺寸:1200×按内容自适应,落在 700-900 高度

不要固定 height 然后用 `align-content: center` 居中——会让画布上下出现大块空白,手机上看就是"这图怎么这么空"。

正确做法:

```css
.page {
  width: 1200px;
  /* 不要写 height */
  padding: 56px 80px 56px;
  display: grid;
  grid-template-rows: auto auto;
  gap: 48px;
}
```

`take_screenshot({ fullPage: true })` 会按内容实际高度截图,自然贴顶贴底,padding 56px 给一点呼吸感就够。

宽度 1200px 在公众号上等比缩放到约 700px 显示,手机上再缩放到屏幕宽度。Retina 屏 2x scale 后是 2400px 宽,文字清晰。

### 信息密度:三块就够,不要更多

公众号读者扫一眼顶图的窗口大约 3-5 秒。能塞进去的有效信息:

| 信息层 | 必要性 | 内容 |
|---|---|---|
| 主标题 | **必须** | 文章主标题(可以和文章 H1 完全相同,也可以是缩写版) |
| 主轴一句 | 强烈推荐 | 一句话点出整篇文章的统一判断 |
| 三阶段 / 三块 / 三步 | 视文章而定 | 每块一个标签 + 一句话(<15 字)说干什么 |

不要塞:

- ❌ 顶栏"ANTHROPIC FIELD NOTES + 日期"——文章正文已经讲了来源
- ❌ 页脚"youtu.be / xxx"——文章末尾来源行已经有
- ❌ kicker "31-MIN WORKSHOP"——多余的元信息
- ❌ 黑色横条"贯穿主轴"——视觉重型,信息上和主轴一句重复
- ❌ 推荐设置区"Opus 4.7 + fast + auto"——读者要拿走时会回正文找
- ❌ bullet 详情列表(每段三条要点)——超过手机扫读窗口
- ❌ 底部细线分隔下的 metadata footer

判断方法:写完一稿,读出每个区块,问"读者扫到这块会带走什么?"。如果答出来的是"哦原来是 Anthropic 的""哦这是 31 分钟的"这种**身份信息**而不是**判断信息**,这块就该删。

---

## 四、视觉设计

### 字体方案要每次换

**强制原则**:不要每次都用同一组字体。AI 生成稿的最大特征是字体趋同(Inter / Space Grotesk / Roboto 全行业撞脸)。每次做摘要图时,换一组陌生组合,刻意避开过往用过的。

记录两组用过的方案,以后避开:

| 方案 | 风格 | Display | Mono | Body | 中文 |
|---|---|---|---|---|---|
| 编辑/技术规范风(信息密集) | 雕刻感、纸质感、有性格 | Fraunces(可变) | JetBrains Mono | Source Serif 4 | fallback 到系统宋体 |
| 报章极简风(留白多) | 古典、克制、清淡 | Cormorant Garamond | IBM Plex Mono | Cormorant + Noto Serif SC | Noto Serif SC |

未来候选(下次轮换时考虑):

- **EB Garamond + DM Mono + Noto Serif SC**(古典报刊)
- **Tenor Sans + JetBrains Mono + Source Han Sans**(瑞士极简)
- **Playfair Display + Space Mono + Noto Serif SC**(对比强烈,沙龙风)
- **Crimson Pro + Geist Mono + Source Han Serif**(现代衬线)
- **Bricolage Grotesque + Berkeley Mono + Source Han Sans**(可变 sans 实验风)

### 中文字体 fallback

绝大部分英文 display 字体不支持中文。中文 fallback 链推荐:

```css
font-family: 'EnglishDisplay', 'Noto Serif SC', 'Songti SC', serif;
```

注意点:

- **不要依赖 italic 给中文加重音**——中文系统字体大多是 fake italic(skew 变形),效果差。改用颜色区分或下划线
- 中文字符在 fallback 字体里通常比英文 display 字符**视觉重量更重**,大标题里中英混排时记得调整字重补偿
- `Source Han Serif`(思源宋体)和 `Noto Serif SC` 是同一字体的不同名字,前者是 Adobe 命名,后者是 Google Fonts 命名

### 配色策略

按信息密度选:

- **信息密集型**:奶油底 + 深墨字 + 一个强调色(陶土橙 / 深绿 / 紫红),色彩做层级标记
- **极简型**:纯白底 + 黑字 + 1px 黑色细线,无色彩。视觉重量全靠 typography + 留白

避免:

- ❌ 紫色渐变(Inter 时代的 AI 标记)
- ❌ 五颜六色的 cell(看起来像 dashboard 不像文章)
- ❌ 深色模式(微信公众号默认浅色,深色顶图和正文反差大)

---

## 五、版面骨架

### 极简版(三块)

```
┌──────────────────────────────────────┐
│                                      │
│   [大标题:中英混排 60-80px]            │
│   ─────────────                     │
│   主轴一句 18-22px                    │
│                                      │
│   ──────────────────────────────    │
│   01      02      03                 │
│   LABEL   LABEL   LABEL              │
│   一句话   一句话    一句话            │
│   ──────────────────────────────    │
│                                      │
└──────────────────────────────────────┘
```

### 信息密集版(三块 + 每块 bullet)

慎用——只在文章本身就是密集方法论且读者会停下来研究图时考虑。手机阅读默认走极简版。

---

## 六、截图实操

```javascript
// 1. 设置 viewport(高度可以预设大一点,fullPage: true 会按内容裁)
await mcp__chrome-devtools__resize_page({ width: 1200, height: 900 });

// 2. 打开本地 HTML
await mcp__chrome-devtools__new_page({
  url: "file:///abs/path/to/summary.html"
});

// 3. 等字体加载(关键!不等会 fallback)
await sleep(2);  // 实际用 Bash 工具 sleep 2

// 4. 全页截图
await mcp__chrome-devtools__take_screenshot({
  filePath: "/abs/path/to/summary-preview.png",
  fullPage: true
});
```

输出大小参考:

| 风格 | viewport | 实际截图 | 文件大小 |
|---|---|---|---|
| 信息密集(陶土橙 + 黑底条 + bullet) | 1200×1456 | 2400×2912 | ~1.2MB |
| 极简(纯白底 + 三块) | 1200×自适应 ≈ 700 | 2400×~1400 | ~200KB |

公众号上传图片有大小限制(通常 5MB / 张),都在范围内,但极简版传得更快、读者加载更快。

### 截图命名

`<日期>-<videoid>-summary.png` 和 `summary.html` 同目录。

---

## 七、嵌入 article.md

主标题之后、第一段之前:

```markdown
# 文章主标题

![文章脉络图:三层进阶 — Prompt 让 Claude 反过来面试 / Spec 用 HTML 替代 Markdown / Artifact 把 verification 烧进契约本身](2026-05-26-IlqJqcl8ONE-summary.png)

第一段开始……
```

**不要**在图片下面加引用块或一段文字解释"图怎么读"。详见 [article-structure.md](article-structure.md) `§2.x 文章顶部信息图本身是论点,不要在图下面写文字注释`。

---

## 八、常见迭代路径(从过往 case 总结)

第一稿 → User feedback → 第二稿 的常见循环:

### 误区 1:第一稿信息密度过高

症状:你把转录里所有有趣的判断都塞进图里。每块三条 bullet,加 kicker,加底栏 stack chips,加黑底引语条。

修法:删到只剩主标题 + 主轴一句 + 三块标签。其他都到正文里去。

### 误区 2:固定画布高度 + align-content: center

症状:图看起来"上下都很空,中间挤一坨"。

根因:你写了 `height: 900px` + `display: grid; align-content: center`。Grid 把所有内容居中,但内容只占 500px 的话,剩下 400px 平均分到上下,各 200px——这就是 user 看到的红框区。

修法:删掉 `height`,让画布按内容自适应。`take_screenshot({ fullPage: true })` 会自动按 DOM 实际高度截图。

### 误区 3:加 header / footer 占空间

症状:画布顶部有"ANTHROPIC · FIELD NOTES + 日期",底部有"How we Claude Code at Anthropic / youtu.be / xxx"。

根因:你想模仿杂志/报刊版式,所以加了 masthead 和 colophon。但顶图不是独立海报,是文章的视觉摘要,身份信息在正文里已经有了。

修法:全删。padding 留 56-80px 让内容有呼吸感就够。

### 误区 4:图片下面写注释

详见 [article-structure.md](article-structure.md) `§2.x`。一句话:让图自己说话。

### 误区 5:每次用同一组字体

详见上面 §四。每次刻意换。

---

## 九、与现有 reference 的关系

- `visual-capture.md` 处理**视频内容截图**(讲者指着的图、代码、UI demo),那是从源视频里截出来的。本文件处理的是**文章顶部摘要图**,是新生成的视觉资产。两者不冲突,通常一篇文章只用其中一种。
- `cover-art-guide.md` 处理**公众号封面图**(列表里显示的小缩略图),那是文章发布时配的另一个素材。摘要图是正文内插图,封面图是 cover.jpg。两者都生成。

工作流:source 字幕 → transcript → article → 摘要图(本文件) + 封面图(cover-art-guide.md)。

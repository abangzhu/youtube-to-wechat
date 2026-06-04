---
name: youtube-to-wechat
description: 把任意来源的内容变成一篇可发布的微信公众号文章，覆盖从字幕提取、原文整理、人物背景、内容分析、中文写作、自审重写到标题和封面图的完整流程。支持 YouTube 视频、网页文章、PDF/Markdown/TXT 本地文档。只要用户提供内容来源（URL、视频链接、文件路径、文本片段），并且目标是中文文章、公众号稿、翻译整理、长文改写、内容总结、视频/文章/PDF 转写，就使用此 skill。
---

# 内容到微信公众号

把 YouTube 视频、网页文章或本地文档转成一篇可发布的中文公众号文章。先获取完整来源，再提炼、写稿、复查和准备发布材料。

## 资源导航

按任务需要读取 reference，避免一次加载全部规则。

| 文件 | 何时读取 |
| --- | --- |
| [references/translation-quality.md](references/translation-quality.md) | 英文来源、双语对照、术语、本地化、翻译腔和事实核查 |
| [references/article-structure.md](references/article-structure.md) | 正文结构、开头、来源交代、段落组织、新概念定义 |
| [references/ai-voice-prohibitions.md](references/ai-voice-prohibitions.md) | **写稿前**扫一遍——词汇级 AI 腔禁词 + 基础句法警示(破折号、强调副词、文学化动词) |
| [references/sentence-level-errors.md](references/sentence-level-errors.md) | **段级精修时**查阅——句法骨架错误、多重定语、词序、表语翻译腔 |
| [references/narration-and-formatting.md](references/narration-and-formatting.md) | **写稿后期**校对——转述腔填充句、标点、引号、加粗、术语书写 |
| [references/self-review.md](references/self-review.md) | 写完 `article.md` 后做读者 / 编辑 / 事实三层评估 + 一份机械 grep checklist |
| [references/title-and-publishing.md](references/title-and-publishing.md) | 拟标题、章节标题、来源注记和发布前检查 |
| [references/youtube-transcript-fallback.md](references/youtube-transcript-fallback.md) | `yt-dlp` 失败、字幕截断、需要时间戳或视频无字幕 |
| [references/visual-capture.md](references/visual-capture.md) | 正文必须插入视频截图、代码画面、架构图、UI 或图表 |
| [references/article-summary-image.md](references/article-summary-image.md) | 文章顶部插入 HTML 渲染的摘要图,适用方法论 / 工作流 / 分层结构类内容 |
| [references/cover-art-guide.md](references/cover-art-guide.md) | 选择封面图路径(抓现成图 vs HTML 模板生成) |
| [references/cover-card-template.md](references/cover-card-template.md) | 用极简纯白卡片模板生成原创封面(含 HTML 模板、字段表、渐变变体、Chrome headless 截图命令) |
| [references/tool-adapters.md](references/tool-adapters.md) | 在 Codex、Claude Code、Cursor 等不同运行环境里选择等价工具 |
| [references/publish-to-notion.md](references/publish-to-notion.md) | 把成稿连文带图发布到 Notion 知识库(Notion MCP 建页 + 分批灌正文 + external 图链 + 图片 ID 映射) |

## 总体流程

1. 获取完整来源，保存原始转录或原文。
2. 整理 `transcript.md` 工作底稿。
3. 调查作者、主播、嘉宾或机构背景。
4. 从来源作者视角和目标读者视角分析内容。
5. 写 `article.md` 初稿。
6. 对照原文检查遗漏的高价值内容。
7. 按三层评估重写，直到通过。
8. 准备标题、章节标题、来源注记和封面图。

## Step 1 获取来源

先判断来源类型。

| 来源类型 | 判断条件 | 路径 |
| --- | --- | --- |
| YouTube 视频 | URL 包含 `youtube.com` 或 `youtu.be` | 路径 A |
| 网页文章 | 其他网页 URL | 路径 B |
| 本地文件 | `.pdf`、`.md`、`.txt`、`.docx` 等文件路径 | 路径 C |
| 文本片段 | 用户直接粘贴内容 | 路径 D |

### 路径 A YouTube 视频

优先用 `yt-dlp` 下载字幕。先尝试中文，再尝试英文。

```bash
yt-dlp --write-auto-sub --sub-lang zh-Hans --skip-download --cookies-from-browser chrome -o "%(title)s" "VIDEO_URL"
yt-dlp --write-auto-sub --sub-lang en --skip-download --cookies-from-browser chrome -o "%(title)s" "VIDEO_URL"
```

如果得到 `.vtt` 文件，用脚本解析：

```bash
python scripts/parse_vtt.py "字幕文件目录路径"
```

`yt-dlp` 失败、字幕缺失、字幕截断、需要时间戳或 YouTube 反爬时，读取 [references/youtube-transcript-fallback.md](references/youtube-transcript-fallback.md)。不要反复尝试该文档列为失效的路径。

英文视频必须生成 `bilingual-transcript.md`。双语对照用于核查翻译质量，不能用 `transcript.md` 替代。格式：

```markdown
[时间戳] 英文原文（逐字保留）

中文忠实译文

---
```

翻译前读取 [references/translation-quality.md](references/translation-quality.md) 的处理层级和翻译前上下文标记。

### 路径 B 网页文章

读取完整正文，保留段落、小节标题、代码块、示例和来源元信息。保存为 `full_transcript_zh.txt` 或 `full_transcript_en.txt`。

如果普通网页抓取只返回摘要、缺少代码块、分页不完整或官方文档被截断，使用可用的浏览器自动化工具提取 `document.body.innerText`，分段保存。不同环境的工具选择见 [references/tool-adapters.md](references/tool-adapters.md)。

### 路径 C 本地文件

读取本地文件完整内容。PDF 较长时分段处理，必要时用 PDF 文本抽取工具保存原始文本。英文 PDF 保存为 `full_transcript_en.txt`，中文文档保存为 `full_transcript_zh.txt`。

### 路径 D 文本片段

把用户粘贴的内容保存为原始底稿。内容较短时仍生成 `transcript.md`，但可以不生成单独的 `full_transcript_*.txt`，除非用户要求可追溯底稿。

## Step 2 生成工作底稿

所有来源都生成 `transcript.md`。底稿要服务写稿，不是简单摘要。保留：

- 作者、主播、嘉宾或机构名字
- 每个话题段的主要论点
- 重要原话
- 关键数字、案例、时间线、产品名和术语
- 来源作者主动强调的判断
- 读者可能直接带走的方法或反常识发现

英文来源整理底稿时同步本地化。读取 [references/translation-quality.md](references/translation-quality.md)，处理术语、缩写、代词、泛指词、长句、主语切换和翻译腔。

内容压缩程度按来源类型决定。访谈、播客和演讲提炼核心论点并保留关键细节。官方文档、产品指南、技术规范和操作手册不能压成摘要，原文有几条建议就保留几条，有示例就保留并翻译。

## Step 3 调查背景

有具体人物时，调查作者、主播和主要嘉宾。匿名文档或纯机构公告可跳过人物小传，改为调查机构、产品或事件背景。

背景调查的目标不是堆简历，而是理解观点从哪里长出来。重点看：

- 成长、教育、职业关键节点
- 思想形成和明显转向
- 公开失败、低谷、代价和反复提到的经历
- 价值观、反对对象和同行位置

输出一份 `background.md` 或放入 `transcript.md` 的背景段。资料丰富时写 1000-2500 字，资料有限时写 300-800 字。

## Step 4 分析内容

按顺序完成三次分析。

第一，来源作者视角。判断他主动选择传递什么，核心论点是什么，用了哪些案例、数据、故事和原话支撑。

第二，读者视角。判断目标读者真正值得带走什么，尤其是反直觉发现、可操作方法、新角色、新工作方式、产品范式、金句和具体判断。

第三,对照原文查漏。逐段检查是否漏掉重要论点、数字、时间线、失败案例、未来判断、关键术语或人物背景里的重要转折。开头钩子和来源交代段最容易翻车,具体陷阱见 [article-structure.md](references/article-structure.md) §3.x「来源交代段最常踩的五条陷阱」+ §3.x.收尾「章节末段最后一句话必须承担收尾力度」。

## Step 5 写 `article.md`

写稿前读取**两份必读** + 一份按需:

- [references/article-structure.md](references/article-structure.md) — 正文结构、开头钩子、来源交代、段落推进
- [references/ai-voice-prohibitions.md](references/ai-voice-prohibitions.md) — 一份词汇级 AI 腔禁词 + 基础句法警示,扫一遍提前规避
- 英文来源再读取 [references/translation-quality.md](references/translation-quality.md)

`sentence-level-errors.md` 和 `narration-and-formatting.md` 留到 Step 6 段级精修和后期校对时再读,这一步还用不上。

文章长度按信息密度决定。30 分钟以内内容通常 1000-1500 字;1 小时左右 1500-2500 字;长访谈、高密度论文、官方指南可超过 2500 字。判断标准是重要观点、案例和证据是否说清楚。

写作要求：

- 开头直接给场景、数字或判断，不先堆简历。
- 自然交代来源、人物和技术背景，但不要把正文写成节目推荐或视频摘要。
- 用连续段落推进，只有长文且主题切换明显时才加 H2。
- 新概念首次出现时给一句中文定义。
- 官方文档和指南类内容必须使用原文示例，不要自行发明例子。
- 英文 prompt、代码块或官方模板保留英文，并在同一个代码块内给中文参考译文。
- 涉及图、代码、UI、架构、流程、表格或屏幕指代时，先放 `[图:MM:SS - 描述]` 占位，并读取 [references/visual-capture.md](references/visual-capture.md)。

## Step 6 自审与重写

写完后读取 [references/self-review.md](references/self-review.md)，按三层检查：

1. 读者视角：标题、开头、段落推进、结尾是否让读者愿意读下去。
2. 编辑视角：结构、语气、AI 腔、转述腔、标点、加粗、术语和截图占位是否合规。
3. 事实视角：专有名词、数字、因果、主语、限定语、翻译和延伸解读是否可追溯。

先做语义自审,再跑 self-review.md 顶部的**机械检查 checklist**(grep 命令直接复制粘贴)。命中后回对应 reference 修正,然后再跑一遍直到全部干净。

**整稿自审通过后,再做一遍段级精修**。整稿审视时大脑在"读完即懂"的速度里跑,会放过开头、第二段、章节衔接段这些高密度位置的深层问题;段级精修时大脑停在每一句话上,卡顿点会被放大。读者也是按段读文章的,在第一段卡住就退出。如果整稿自审只发现 0-1 个改动点,基本可以肯定段级精修还能挖出 3-5 个。段级精修必查项(无 grep 触发词的句法 / 词序问题)见 self-review.md「段级精修必查清单」,需要查阅深度规则时打开 [sentence-level-errors.md](references/sentence-level-errors.md);最后做格式校对时打开 [narration-and-formatting.md](references/narration-and-formatting.md)。整体方法见 [article-structure.md §3.y「段级互动重写比一次性整稿改更准」](references/article-structure.md)。

协作场景里,鼓励用户做"段级反馈"——一段一段问"这段怎么样",而不是"整篇怎么样"。

## Step 7 标题与发布准备

定稿后读取 [references/title-and-publishing.md](references/title-and-publishing.md)。

先写一句话锚定原文主旨，再拟 3-5 个标题。标题要和原文主旨一致，不为结构感硬凑数字清单，也不为反差感硬造二元对比。

除非用户已经明确指定标题，否则先展示标题备选，不要擅自覆盖 `article.md` 第一行。用户确认后再写入：

```markdown
# 标题
```

封面图先选路径:**A. 抓取现成图**(YouTube 缩略图 / 网页 og:image / 文档截图)或 **B. HTML 模板生成原创卡片**(极简纯白 + 厚字重 + 可选渐变)。

按内容类型选:

- 访谈现场、嘉宾正脸、产品 demo 截图、关键图表 → **A**(现场画面本身就是钩子)
- 观点解读、方法论综述、12 条预测、思考长文 → **B**(画面要传达主旨而非来源)
- 数据报告、行业分析、技术深度 → 视来源决定:有强图表用 A,纯文字用 B
- 哲学评论、文化随笔、文学性文章 → **B**(选 `claude-design-card` 那一脉的暖底衬线)

两种路径的判断标准和实现见 [references/cover-art-guide.md](references/cover-art-guide.md);路径 B 的完整模板见 [references/cover-card-template.md](references/cover-card-template.md)。

如果文章主题是方法论 / 工作流 / 分层结构 / 多阶段进阶,考虑在文章顶部加一张 HTML 渲染的摘要图作为视觉锚点(用 frontend-design + Chrome DevTools 截图)。这件事本身就是一种"实操即论证"的动作——用 HTML spec 形式呈现文章结构。流程见 [references/article-summary-image.md](references/article-summary-image.md)。

## Step 8 发布到 Notion（按需）

用户要求把成稿连文带图发布 / 上传到 Notion 知识库时（如「放到 Notion 写作/AI/Blog 转载目录下」），读取 [references/publish-to-notion.md](references/publish-to-notion.md)。要点：Notion MCP 的块类型 schema 是简化的但实际透传完整类型；本地图片不能上传，来源若有公网图 URL（`source.json` / og:image / X CDN）就用 external image block 直接引用；图片用 alt 里的 media ID 映射到 URL，不要按文件名顺序硬配；正文分批 `patch-block-children`。

## 输出文件

| 文件 | 内容 | 何时生成 |
| --- | --- | --- |
| `full_transcript_en.txt` / `full_transcript_zh.txt` | 原始来源文本 | YouTube 必做;网页 / 本地文件按需(用户要求可追溯底稿时) |
| `bilingual-transcript.md` | 英文原文 + 中文忠实译文 | 英文 YouTube 必做;用户要求忠实翻译时必做 |
| `transcript.md` | 结构化工作底稿 | 所有来源必做 |
| `background.md` | 人物、机构或事件背景 | 来源里有具体人物(嘉宾、作者),且其经历对理解观点是必要时生成;匿名文档 / 纯机构公告跳过 |
| `article.md` | 最终公众号文章 | 所有来源必做 |
| `title-options.md` | 3-5 个标题备选 | 定稿前生成,展示给用户挑选 |
| `<VIDEO_ID>-frame-<MMSS>.jpg` | 视频截图 | 正文里出现「这张图 / 这段代码 / 屏幕上」等 deixis 指示语,且抽掉截图后段落看不懂时生成 |
| `<日期>-<VIDEO_ID>-summary.html` / `summary.png` | 文章顶部摘要图(HTML 源 + 渲染截图) | 文章主题是方法论 / 工作流 / 分层结构 / 多阶段进阶,用一张图能概括全文骨架时生成 |
| `cover.jpg` | 封面图 | 所有来源都做。Path A 抓现成图,Path B 用 HTML 模板生成 |

如果当前目录已有同名文件且明显属于其他任务，使用来源 slug 前缀，例如 `mcp-future-article.md`。

文章末尾必须注明来源。格式按类型选择：

```markdown
内容来源，[频道名称]「[视频标题]」，YouTube 链接 [URL]，嘉宾为 [嘉宾名称]。
内容来源，[作者]「[文章标题]」，原文链接 [URL]，发布于 [平台/媒体名称]。
内容来源，[作者 / 机构]「[文档标题]」，[发布日期或版本号]。
```

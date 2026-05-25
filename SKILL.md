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
| [references/style-and-ai-voice.md](references/style-and-ai-voice.md) | 公众号语气、AI 腔、翻译腔、元评论、标点、加粗和术语写法 |
| [references/self-review.md](references/self-review.md) | 写完 `article.md` 后做读者、编辑、事实三层评估 |
| [references/title-and-publishing.md](references/title-and-publishing.md) | 拟标题、章节标题、来源注记和发布前检查 |
| [references/youtube-transcript-fallback.md](references/youtube-transcript-fallback.md) | `yt-dlp` 失败、字幕截断、需要时间戳或视频无字幕 |
| [references/visual-capture.md](references/visual-capture.md) | 正文必须插入视频截图、代码画面、架构图、UI 或图表 |
| [references/cover-art-guide.md](references/cover-art-guide.md) | 生成或截取封面图 |
| [references/tool-adapters.md](references/tool-adapters.md) | 在 Codex、Claude Code、Cursor 等不同运行环境里选择等价工具 |

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

第三，对照原文查漏。逐段检查是否漏掉重要论点、数字、时间线、失败案例、未来判断、关键术语或人物背景里的重要转折。

## Step 5 写 `article.md`

写稿前读取：

- [references/article-structure.md](references/article-structure.md)
- [references/style-and-ai-voice.md](references/style-and-ai-voice.md)
- 英文来源再读取 [references/translation-quality.md](references/translation-quality.md)

文章长度按信息密度决定。30 分钟以内内容通常 1000-1500 字；1 小时左右 1500-2500 字；长访谈、高密度论文、官方指南可超过 2500 字。判断标准是重要观点、案例和证据是否说清楚。

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

先做语义自审，再跑 grep 级兜底。发现问题后直接重写，不只替换触发词。重写完成后再做一轮检查。

## Step 7 标题与发布准备

定稿后读取 [references/title-and-publishing.md](references/title-and-publishing.md)。

先写一句话锚定原文主旨，再拟 3-5 个标题。标题要和原文主旨一致，不为结构感硬凑数字清单，也不为反差感硬造二元对比。

除非用户已经明确指定标题，否则先展示标题备选，不要擅自覆盖 `article.md` 第一行。用户确认后再写入：

```markdown
# 标题
```

封面图按来源选择。YouTube 优先抓视频封面；网页抓 `og:image`；本地文件按内容截图或生成封面。细节见 [references/cover-art-guide.md](references/cover-art-guide.md)。

## 输出文件

| 文件 | 内容 | 何时生成 |
| --- | --- | --- |
| `full_transcript_en.txt` / `full_transcript_zh.txt` | 原始来源文本 | YouTube 必做，其他来源按需 |
| `bilingual-transcript.md` | 英文原文 + 中文忠实译文 | 英文 YouTube 必做，用户要求忠实翻译时必做 |
| `transcript.md` | 结构化工作底稿 | 所有来源必做 |
| `background.md` | 人物、机构或事件背景 | 有人物或重要背景时生成 |
| `article.md` | 最终公众号文章 | 所有来源必做 |
| `title-options.md` | 3-5 个标题备选 | 定稿前生成 |
| `<VIDEO_ID>-frame-<MMSS>.jpg` | 视频截图 | 仅正文需要视觉锚点时生成 |
| `cover.jpg` | 封面图 | 发布准备阶段生成 |

如果当前目录已有同名文件且明显属于其他任务，使用来源 slug 前缀，例如 `mcp-future-article.md`。

文章末尾必须注明来源。格式按类型选择：

```markdown
内容来源，[频道名称]「[视频标题]」，YouTube 链接 [URL]，嘉宾为 [嘉宾名称]。
内容来源，[作者]「[文章标题]」，原文链接 [URL]，发布于 [平台/媒体名称]。
内容来源，[作者 / 机构]「[文档标题]」，[发布日期或版本号]。
```

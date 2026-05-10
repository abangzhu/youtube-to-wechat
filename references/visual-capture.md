# 可视化段落的截图流程

文字表达不清楚的地方，文章里插图；图来源是原视频对应时间点的截图。本文件讲三件事：什么时候需要图、从 YouTube 截图的精确流程、图怎么插进 `article.md`。

---

## 一、什么时候必须插图

转录里有大量 deixis（指示语）——讲者在屏幕前用手比划或者直接指代 slide。这些表达在现场是充分的，进到文章里却完全悬空，读者没有任何视觉锚点。出稿时遇到下面这些信号，记下时间戳，准备截图：

- 讲者提到「这张图」「这根箭头」「这个方框」「这个流程」「这个 demo」「这段代码在屏幕上」「这条曲线」「这个表格」
- 讲者在讲架构图、流程图、状态机、对比表、数据曲线、UI 截图，而这些图正是他的核心论点依托
- 讲者演示 CLI / 终端输出 / 代码片段 / 错误信息，文字描述还原不出完整视觉
- 数据可视化（柱状图、散点图、时间序列），光靠数字读者脑补不出关系
- 产品界面截图，新产品 / 新功能的 UI 是读者没见过的

反之，这些情况不需要截图：

- 讲者只是说了一句金句，没有配图
- 讲者在讲纯文字要点（没有屏幕支持）
- 讲者的 slide 只是一行文字标题，截图没有额外信息量
- 讲者在白板上手写，画面很糊或者反光严重

判断标准：如果读者看不到这张图，文章这一段的理解会不会打折？会打折就截。

---

## 二、从 YouTube 精确截图的流程

工具：Chrome DevTools MCP。比 yt-dlp 下载整段视频再 ffmpeg 抽帧稳得多（yt-dlp 在 SABR 限制下经常失败），而且直接在浏览器里精确定位到帧，画质是 YouTube 解码后的原始像素。

### Step 1：打开视频并定位到时间点

用 `mcp__chrome-devtools__new_page` 打开带时间戳参数的 URL。YouTube 的时间参数格式是 `?t=Ns` 或 `?t=MMmSSs`，其中 N 是总秒数。

```
URL 示例:
https://www.youtube.com/watch?v=ynJyIKwjonM&t=141s   ← 2:21
https://www.youtube.com/watch?v=ynJyIKwjonM&t=2m21s  ← 同上，写法二
```

从转录时间戳换算总秒数：`02:21` → 2×60+21 = 141 秒。

### Step 2：等视频加载并暂停在指定帧

视频打开默认会自动播放。等待 2-3 秒让它解码到那一帧，然后暂停在对的一帧上。用 `mcp__chrome-devtools__evaluate_script` 精确控制：

```javascript
() => {
  const v = document.querySelector('video');
  if (!v) return { error: 'video element not found' };
  // 强制跳到指定秒数，避免视频自己播飘了
  v.currentTime = 141;
  v.pause();
  return {
    currentTime: v.currentTime,
    paused: v.paused,
    readyState: v.readyState,  // 4 表示可以截图了
    duration: v.duration
  };
}
```

`readyState >= 3` 意味着当前帧已经解码好可以截了。如果返回 `readyState < 3`，再 `sleep 1` 重跑一次脚本确认。

### Step 3：隐藏 YouTube 控件再截图

YouTube 播放器暂停时会叠加一层控件遮挡画面。截图前先把鼠标移出视频区域，或者直接注入 CSS 把控件隐掉：

```javascript
() => {
  const style = document.createElement('style');
  style.id = 'hide-yt-controls';
  style.textContent = `
    .ytp-chrome-bottom, .ytp-gradient-bottom, .ytp-chrome-top,
    .ytp-pause-overlay, .ytp-ce-element, .ytp-suggestion-set,
    .ytp-endscreen-content, .ytp-cards-teaser, .ytp-scroll-min {
      display: none !important;
    }
    video::-webkit-media-controls { display: none !important; }
  `;
  document.head.appendChild(style);
  return 'controls hidden';
}
```

### Step 4：截图到文件

用 `mcp__chrome-devtools__take_screenshot`，指定 `uid` 为 video 元素可以只截视频区域。如果只需要整页截图，省略 `uid` 参数。

文件名规范：`<VIDEO_ID>-frame-<MMSS>.jpg`，例如 `ynJyIKwjonM-frame-0221.jpg`。放在和 article.md 同一目录下，保持相对路径引用简单。

```
mcp__chrome-devtools__take_screenshot
  filePath: "ynJyIKwjonM-frame-0221.jpg"
  format: "jpeg"
  quality: 90
```

如果你想只截视频区域（推荐）：先用 `take_snapshot` 拿到 video 元素的 uid，再用那个 uid 截图。整页截图包含 YouTube 推荐栏、评论区，信息密度低。

### Step 5：多张图批量处理

如果同一篇文章需要 3-5 张截图，不要每张都新开一个 page。在同一个页面里依次 `evaluate_script` 调整 `currentTime` 到下一个时间戳，暂停，截图，重复。把所有截图指令一次列好再执行，效率高得多。

---

## 三、图插进 `article.md` 的写法

Markdown 语法：

```markdown
![这张图里左边是 Context 源，右边是 Context Window，中间那根小箭头 Leonie 认为才是整件事的核心](ynJyIKwjonM-frame-0221.jpg)
```

三件事：

1. **alt 文字要写全，不要留空或只写 "image"**。微信公众号后端会用 alt 文字做图片无障碍描述，读者在某些场景（纯文本客户端、慢网络）也会看到。alt 要能替代图片讲出这一段想表达的东西。
2. **图在相关段落之后，不要在段落中间**。先把判断写完，然后贴图作为视觉印证，读者的阅读节奏是"读一段话 → 看图 → 读下一段话"。
3. **不要把图当论据替身**。图是辅助说明，不是省略文字的理由。"Leonie 的暴论是这根箭头才是整件事的核心" + 插图，这样写是对的；但不能只插一张图然后写一句"如图"就完事。文字该讲的判断还是要讲。

### 段落和图的典型搭配

**架构 / 流程类**：讲者提到某种架构的组成部分，先用一两句话描述每个部分，再插图。例如讲 Context Engineering 的时候，文字说清"左边源、右边窗口、中间箭头"，再贴图让读者对应上去。

**对比表类**：讲者展示了一张表格对比几个方案，先在文字里列出几条关键差异，再贴表格图。读者看文字抓到主线，看图抓到细节。

**代码 / 终端类**：讲者演示 CLI 交互，如果关键是输出内容（比如 Agent 连环 grep 同义词那一段），可以直接把输出截图。如果关键是代码本身，考虑是用图还是用代码块 —— 代码块复制性更好，图还原现场感更好，两种都可选。

**产品界面**：新产品 UI 第一次出现时必须贴图，后面如果还有就不用每次都贴。

### 反例对照

- 坏：文章里写「她展示了一张图，图里解释了 Context 源到 Context Window 的流向」然后没图。读者脑子里完全空白。
- 好：文章里写「她的那张图很简单：左边是各种 Context 源，右边是 Context Window，中间一根小箭头负责把东西搬过去。Leonie 的暴论是，这根小箭头才是整件事的核心。」+ 插图。读者有文字抓手，图是印证。

---

## 四、实操节奏

写初稿时，遇到需要可视化的地方不要打断写作节奏去截图，先在正文用 `[图:MM:SS - 描述]` 占位。举例：

```
她的那张图很简单，左边是各种 Context 源，右边是 Context Window，中间一根小箭头负责把东西搬过去。[图:02:21 - Context Engineering 流向示意图]
```

一段初稿写完（或整篇写完），再集中用 Chrome DevTools MCP 打开视频，依次定位到每个时间戳截图，然后回到 article.md 把占位符替换成 Markdown 图片语法。这样写作节奏不被中断，截图可以批量化。

截图文件要和 `article.md` 放在同一个目录下，相对路径引用 `![描述](ynJyIKwjonM-frame-0221.jpg)` 就能在 Obsidian 和微信公众号编辑器里正确显示。上传到公众号时编辑器会自动把本地图片转成微信 CDN 链接。

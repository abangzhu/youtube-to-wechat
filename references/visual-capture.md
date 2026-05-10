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

核心做法是 `take_screenshot(uid="<video-element-uid>")` —— 把 video DOM 元素的 uid 传给 take_screenshot，它会只截那个元素的 bounding box，而不是整个 viewport。这样截出来的图就是干净的视频画面，没有 YouTube 右侧推荐栏、评论区、控件叠加层。画质是实际显示尺寸 × devicePixelRatio，比视频原生 1280×720 常常还更清晰。

**避坑提示**：不要用 `canvas.drawImage(video, 0, 0) + canvas.toDataURL()` 这套方案。在 YouTube 的 video 元素上，`drawImage` 的行为经测试并不会只画视频帧像素，导出的 base64 解码后仍带着 YouTube 页面 UI。浪费时间，直接走 uid 路线。

### Step 1：打开视频并定位到时间点

用 `mcp__chrome-devtools__new_page` 打开带时间戳参数的 URL。YouTube 的时间参数格式是 `?t=Ns` 或 `?t=MMmSSs`，其中 N 是总秒数。

```
URL 示例：
https://www.youtube.com/watch?v=ynJyIKwjonM&t=141s   （2:21）
https://www.youtube.com/watch?v=ynJyIKwjonM&t=2m21s  （同上，写法二）
```

从转录时间戳换算总秒数：`02:21` → 2×60+21 = 141 秒。

如果 `new_page` 超时（YouTube 首屏慢，10 秒超时常发生），不用管。用 `list_pages` 找到带 `&t=` 的那个 tab，`select_page` 到它上面继续操作。

### Step 2：跳到指定帧并暂停

视频打开默认自动播放。用 `evaluate_script` 强制跳到目标秒数并暂停：

```javascript
() => {
  const v = document.querySelector('video');
  if (!v) return { error: 'video element not found' };
  v.currentTime = 141;
  v.pause();
  return {
    currentTime: v.currentTime,
    paused: v.paused,
    readyState: v.readyState,
    videoWidth: v.videoWidth,
    videoHeight: v.videoHeight
  };
}
```

`seek` 之后 `readyState` 通常会掉到 1（数据还在解码），等 2 秒后再查一次，`readyState === 4` 就可以截了。

### Step 3：拿到 video 元素的 uid

用 `mcp__chrome-devtools__take_snapshot`。在返回的 a11y tree 里找 `uid=X_Y Video` 这一行，那就是主视频元素的 uid。在本次样本里它是 `1_17`，实际每个 session 可能不同，用完就丢。

### Step 4：截图到 video 的 uid

```
mcp__chrome-devtools__take_screenshot
  filePath: "ynJyIKwjonM-frame-0221.jpg"
  format: "jpeg"
  quality: 92
  uid: "1_17"
```

关键是 **`uid` 参数必须带上**。不带 uid，take_screenshot 默认截整个 viewport，你会得到 YouTube 完整 UI + 视频缩略版混在一起的难看的图。

文件名规范：`<VIDEO_ID>-frame-<MMSS>.jpg`，例如 `ynJyIKwjonM-frame-0221.jpg`。放在和 `article.md` 同一目录下，相对路径引用简单。

**注意**：take_screenshot 写出来的文件扩展名可能是 `.jpeg`（即使你在 filePath 里写了 `.jpg`，它会按 format 字段自动补一次扩展名）。加一步 `mv foo.jpeg foo.jpg` 把扩展名规整成 `.jpg` 和 article 里的 Markdown 引用一致。

### Step 5：多张图批量处理

同一篇文章要 3-5 张截图，**不要**每张都 `new_page`。在同一个 tab 里循环：`evaluate_script` 调 `currentTime` → 等 2 秒解码 → 再 `evaluate_script` 确认 `readyState === 4` → `take_screenshot(uid=同一个 video uid)` → 换下一个时间戳重复。video 元素的 uid 在同一个 tab 里不变，`take_snapshot` 只需要做一次。

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

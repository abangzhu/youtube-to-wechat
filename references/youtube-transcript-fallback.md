# YouTube 字幕提取备用路径

yt-dlp 失败时按以下顺序尝试。第一选择是 kome.ai（最快、无依赖），需要时间戳时切到 tactiq。

## 触发条件

yt-dlp 报以下错误之一时，说明被 YouTube 的 SABR 流式传输限制或 PO Token 要求拦住，无法直接下载字幕：

- `Some web client https formats have been skipped`
- `Requested format is not available`
- `Some mweb client subtitles require a PO Token which was not provided`
- `There are missing subtitles languages because a PO token was not provided`
- `n challenge solving failed: Some formats may be missing. Ensure you have a supported JavaScript runtime and challenge solver script distribution installed`（2026 年起常见）
- `Sign in to confirm you're not a bot`（即使加了 `--cookies-from-browser chrome` 仍报这条，说明 cookies 没救）

这些错误出现时，字幕本身可能存在于 YouTube，只是 yt-dlp 拿不到。区分这两种情况是选路径的关键。

**跳过浪费时间的尝试**：以下三条路径在最近的实战中已经基本失效，不要先试再说：

- `https://youtubetranscript.com/?server_vid2=<id>` 直接返回 "We're sorry, YouTube is currently blocking us from fetching subtitles"
- `youtube-transcript-api`（Python 包）报 `RequestBlocked`，YouTube 在 IP 层 block 了它的服务器段
- `https://get-info.downsub.com/<id>` 对参数格式很挑，且核心字幕仍走 YouTube 接口，被同源策略影响

---

## 方法 A：kome.ai HTTP POST（首选，最快、无 Chrome 依赖）

`https://kome.ai/api/transcript` 是一个无认证、无登录的 HTTP POST 接口，curl 一行就能拿到完整字幕。耗时一般在 2-5 秒。**唯一缺点是没时间戳**。

如果文章不需要截图（演讲讲的全是抽象内容、没有「这张图」「这段代码」这种 deixis 指示语），方法 A 就是最优路径。如果文章可能要截图，跳到方法 B。

### 步骤

```bash
curl -sL -X POST "https://kome.ai/api/transcript" \
  -H "Content-Type: application/json" \
  -d '{"video_id":"<完整 YouTube URL>","format":true}' \
  -o /tmp/kome.json
```

参数说明：
- `video_id` 字段名是这样，但**值要传完整 URL**（`https://youtu.be/XXX` 或 `https://www.youtube.com/watch?v=XXX`），不是单独的 video ID
- `format=true` 给段落分行；`format=false` 给一整行无换行的纯文本

返回的 JSON 结构：

```json
{
  "transcript": "...完整字幕文本...",
  "length": "18m 11s",
  "hasMore": false,
  "isPremium": false
}
```

提取并保存：

```python
import json
with open('/tmp/kome.json') as f:
    d = json.load(f)
text = d['transcript']
with open('<日期>-<videoid>-full_transcript_en.txt', 'w') as f:
    f.write(text)
```

### 验证字幕完整性

`hasMore` 字段是关键。如果 `hasMore: false` 且 `length` 与视频实际时长一致，字幕完整。如果 `hasMore: true`，说明免费档被截断了，切到方法 B 拿完整版。

也对比一下 `len(transcript)` 和视频时长，演讲类视频每分钟大约 700-1000 字符（英文）。1 小时演讲不到 30000 字符就可能被截。

### 什么时候方法 A 会失败

| 现象 | 原因 | 解法 |
|------|------|------|
| `transcript` 字段是错误信息或为空 | kome 也被限速或视频无字幕 | 切方法 B 或方法 C |
| `hasMore: true` 截断 | 免费档限制 | 切方法 B 拿完整版 |
| HTTP 500/429 | 服务暂时性故障 | 等 30 秒重试一次；仍失败切方法 B |

### 后续生成 bilingual-transcript.md 的注意事项

kome 输出无时间戳。生成双语对照时按段落分组、用 `[Intro 1]` `[Boss 1 - 2]` 这类语义标签替代时间戳。下游 `transcript.md` 不受影响。

---

## 方法 B：tactiq.io + Chrome DevTools MCP（需要时间戳时用）

tactiq.io 在浏览器端请求字幕，能绕开 yt-dlp 遇到的 PO Token 限制，**输出带时间戳**（每段两行，第一行 `HH:MM:SS.fff`，第二行文本）。需要 Chrome DevTools MCP 在线。

如果 Chrome DevTools MCP 报 `Network.enable timed out` 持续超过 30 秒，说明 MCP 服务自身有问题。等不动就直接退到方法 A（接受没时间戳）或方法 C。

### 步骤

1. 从视频 URL 提取 video ID（例如 `ow1we5PzK-o`）
2. 用 Chrome DevTools MCP `new_page` 打开：
   ```
   https://tactiq.io/tools/run/youtube_transcript?yt=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{VIDEO_ID}
   ```
   `yt` 参数是完整 YouTube URL 做 URL encoding 后的结果
3. 页面加载后等 3-5 秒（tactiq 后台解析字幕）
4. `evaluate_script` 提取 `#transcript` 的 innerText：
   ```javascript
   () => {
     const el = document.querySelector('#transcript');
     if (!el) return 'ERROR: transcript container not found';
     const text = el.innerText;
     if (text.length < 50) return 'EMPTY: video likely has no captions on YouTube';
     return text;
   }
   ```
5. 输出格式是每段两行，第一行时间戳，第二行文本。保存为 `<日期>-<videoid>-full_transcript_<lang>.txt`

### 注意：不要 curl tactiq

tactiq 的 transcript 是 JS 异步渲染的，HTML 骨架里 `#transcript` 是空 div。直接 `curl https://tactiq.io/tools/run/youtube_transcript?...` 拿到的页面里只有壳子，必须走 Chrome DevTools MCP 才能拿到 JS 注入后的内容。

### 示例典型输出

```
00:00:07.205
[music]
00:00:15.040
>> Hi everyone. My name is Luke and my goal
00:00:18.240
is that 20 minutes from now you'll be
```

直接当作原始转录处理即可。整理成 `transcript.md` 时把相邻短段合成段落。

### 什么时候方法 B 会失败

- `#transcript` 在 10 秒后仍为空字符串。说明 YouTube 端这个视频确实没有任何字幕（tactiq 不做 ASR，只搬运 YouTube 的字幕流）
- Chrome DevTools MCP 长时间 `Network.enable timed out`。这是 MCP 服务问题，不是字幕问题。回退到方法 A
- 这两种情况下方法 C 也不会成功，直接跳到「确实无字幕的处理」一节

---

## 方法 C：Chrome DevTools MCP fetch 拦截器（方法 A、B 都失败但视频确实有字幕时用）

方法 A、B 已经够用，这里保留只是以防 kome 和 tactiq 同时下线。如果前两条能跑，不要切到这条路，它更麻烦、更容易出错。

### ⚠️ 核心约束

**拦截器必须在点击字幕按钮之前注入。顺序不能颠倒。**

如果先点了 Show transcript，请求已经发出，再注入拦截器也捕获不到数据，需要重新加载页面从头来。

### 步骤一：打开视频，立刻注入 fetch 拦截器

用 Chrome DevTools MCP `new_page` 打开视频 URL，页面加载完成后立刻执行：

```javascript
() => {
  const origFetch = window.fetch;
  window.fetch = async function(...args) {
    const response = await origFetch.apply(this, args);
    const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
    if (url.includes('get_transcript') || url.includes('youtubei')) {
      try {
        const clone = response.clone();
        const data = await clone.json();
        if (JSON.stringify(data).includes('transcriptSegmentRenderer')) {
          window._transcriptData = data;
        }
      } catch(e) {}
    }
    return response;
  };
  return 'interceptor ready';
}
```

确认返回值是 `"interceptor ready"` 再继续。

### 步骤二：点击 Show transcript 按钮

取页面快照，找到 Show transcript 按钮（通常在视频描述区域右侧，或点击 ⋯ More 展开菜单），点击它触发字幕请求。

### 步骤三：提取字幕文本

```javascript
() => {
  const data = window._transcriptData;
  if (!data) return 'ERROR: No transcript data — was interceptor injected before clicking?';
  const segments = data?.actions?.[0]?.updateEngagementPanelAction?.content
    ?.transcriptRenderer?.content?.transcriptSearchPanelRenderer
    ?.body?.transcriptSegmentListRenderer?.initialSegments;
  if (!segments) return 'ERROR: Segments path not found, check JSON structure';

  const lines = [];
  for (const seg of segments) {
    if (seg.transcriptSectionHeaderRenderer) {
      const label = seg.transcriptSectionHeaderRenderer?.accessibility?.accessibilityData?.label;
      if (label) lines.push('\n## ' + label + '\n');
    }
    if (seg.transcriptSegmentRenderer) {
      const r = seg.transcriptSegmentRenderer;
      const seconds = Math.floor(parseInt(r.startMs) / 1000);
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      const ts = `${mins}:${String(secs).padStart(2, '0')}`;
      const text = (r?.snippet?.runs || []).map(run => run.text).join('');
      if (text.trim()) lines.push(`[${ts}] ${text}`);
    }
  }
  return lines.join('\n');
}
```

### 方法 C 排错

| 现象 | 原因 | 解法 |
|------|------|------|
| 步骤三返回 `"ERROR: No transcript data"` | 拦截器注入前字幕请求已发出 | 重新加载页面，重新执行步骤一，再点字幕按钮 |
| 步骤三返回 `"ERROR: Segments path not found"` | YouTube API 结构发生变化 | 执行 `() => JSON.stringify(Object.keys(window._transcriptData?.actions?.[0] ?? {}))` 探查新路径 |
| 字幕按钮不可见 | 视频没有字幕，或按钮在 ⋯ More 菜单内 | 展开菜单后再找；按钮真的没有，切到「确实无字幕」一节 |

---

## 确实无字幕的处理

方法 A 返回错误或空、方法 B 看不到字幕按钮、YouTube 播放器显示 "Subtitles/closed captions unavailable"——这些都说明视频真的没字幕。通常发生在刚直播完不到 24 小时的视频，YouTube 的自动字幕还没生成出来。

此时免费路径全部失效，所有第三方转录服务（kome、tactiq、downsub、NoteGPT 免费档、youtubetranscript.com）都依赖 YouTube 原生字幕，都取不到。NoteGPT 付费档有自己的 ASR，但需要登录 + 信用卡。

### 推荐动作

使用当前环境可用的用户确认工具，让用户在以下路径中选；没有结构化提问工具时，用简短自然语言提问：

1. **基于二手资料写文章**：用 WebSearch 查这个视频/演讲的媒体报道、官方博客、嘉宾个人博客、liveblog、事件新闻稿。如果是知名会议或公司公告，官方博客往往有详细文字版。成文时透明交代「视频暂无字幕，本文基于 X、Y、Z 公开资料综合」
2. **等 24-48 小时**：YouTube 自动字幕通常在直播结束后 1-2 天内生成，让用户明天再来跑流程
3. **用户自备转录**：如果用户有内部渠道（付费转录、会议纪要、演讲稿），让用户提供文件路径或粘贴文本，按本地文件路径（路径 C）处理
4. **换视频**：如果只是想要一篇关于该主题的文章，换一个有字幕的同主题视频

不要静默降级去跑二手资料路径，这会让用户以为你真的看过了视频内容。先告知限制，拿到明确选择再继续。

---

## 决策速查表

| 情况 | 路径 | 是否带时间戳 |
|------|------|--------------|
| yt-dlp 成功 | 用 yt-dlp 结果 | 是 |
| yt-dlp 失败，文章不需要截图 | 方法 A（kome.ai） | 否 |
| yt-dlp 失败，文章需要截图（有 deixis 指示语） | 方法 B（tactiq + Chrome DevTools） | 是 |
| 方法 A、B 都失败，视频播放器显示「字幕可用」 | 方法 C（fetch 拦截器） | 是 |
| 方法 A 返回错或截断、方法 B 返回空、YouTube 显示「Subtitles/closed captions unavailable」 | 走「确实无字幕的处理」 | — |
| Chrome DevTools MCP 持续 `Network.enable timed out` | 直接走方法 A，接受没时间戳 | 否 |

## 关于「是否需要截图」的判断

这条决策决定了选方法 A 还是方法 B：

- **不需要截图的视频**：纯讲述、抽象方法论、不依赖屏幕内容（比如哲学对谈、产品理念演讲、远程访谈等）
- **需要截图的视频**：架构图讲解、代码 walkthrough、UI 演示、对比表格、流程图——讲者用「这张图」「这条线」「屏幕上」「这段代码」等 deixis 指示语锚定到画面

判断不准时优先方法 B 拿时间戳，写作时再决定用不用。但如果 Chrome DevTools MCP 当时挂了，方法 A 拿到字幕先把文章写出来，截图缺失这件事比拿不到字幕事小。

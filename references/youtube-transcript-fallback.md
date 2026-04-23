# YouTube 字幕提取备用路径：Chrome DevTools MCP

当 yt-dlp 报以下错误时使用此路径：

- `Some web client https formats have been skipped`
- `Requested format is not available`

这是 YouTube SABR（Server-Abridged Bitrate Representation）流式传输限制导致的，yt-dlp 无法绕过。

## ⚠️ 核心约束

**拦截器必须在点击字幕按钮之前注入。顺序不能颠倒。**

如果先点了字幕按钮，请求已经发出，再注入拦截器也捕获不到数据，需要重新加载页面从头来。

---

## 步骤一：打开视频，立刻注入 fetch 拦截器

用 Chrome DevTools MCP `new_page` 打开视频 URL，页面加载完成后，**在做任何其他操作之前**执行以下脚本：

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

---

## 步骤二：点击 Show transcript 按钮

取页面快照，找到 "Show transcript" 按钮（通常在视频描述区域右侧，或点击 `⋯ More` 展开菜单），点击它触发字幕请求。

---

## 步骤三：提取字幕文本

执行以下脚本提取完整字幕（含章节标题和时间戳）：

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

将输出写入 `full_transcript_en.txt`。

---

## 排错

| 现象 | 原因 | 解法 |
|------|------|------|
| 步骤三返回 `"ERROR: No transcript data"` | 拦截器注入前字幕请求已发出 | 重新加载页面，重新执行步骤一，再点字幕按钮 |
| 步骤三返回 `"ERROR: Segments path not found"` | YouTube API 结构发生变化 | 执行 `() => JSON.stringify(Object.keys(window._transcriptData?.actions?.[0] ?? {}))` 探查新路径 |
| 字幕按钮不可见 | 视频没有字幕，或按钮在 `⋯ More` 菜单内 | 展开菜单后再找 |

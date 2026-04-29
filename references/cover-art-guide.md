# 封面图获取指南

---

## YouTube 视频

**方法一：curl 直接下载（最稳定，优先用）**

YouTube 缩略图有固定 URL 格式，不需要 yt-dlp，直接 curl：

```bash
# 替换 VIDEO_ID 为视频 URL 中 ?v= 后面的部分（如 v3Fr2JR47KA）
curl -L -o cover.jpg "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg"
```

不受 SABR 流式传输影响，始终可用。`maxresdefault.jpg` 通常是 1280×720。

**方法二：yt-dlp 下载缩略图**

```bash
yt-dlp --write-thumbnail --skip-download \
  --cookies-from-browser chrome \
  -o "cover" \
  "VIDEO_URL"
```

输出 `cover.webp` 或 `cover.jpg`。如果报 SABR 相关错误（`Requested format is not available`），改用方法一。

**方法三：截取指定帧**（想要特定画面时）

用 Chrome DevTools MCP 打开视频，拖动进度条到合适位置暂停，截图保存为 `cover.png`。选嘉宾正脸清晰、有表情或动作的帧，或者有文字画面感的关键时刻，避开片头片尾和黑屏。

---

## 网页文章

大多数文章页面有 Open Graph 图片，适合直接做封面：

```bash
# 用 curl 查看 og:image meta 标签
curl -s "ARTICLE_URL" | grep -i 'og:image'
```

如果 OG 图片质量不佳，用 Chrome DevTools MCP 截取文章首屏或文中核心图表。

---

## 本地文件

PDF / Markdown 通常没有配套图片，建议从文档内容中选取有代表性的图表截图，或根据文章主题自行准备封面图。

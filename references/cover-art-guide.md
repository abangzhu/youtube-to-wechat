# 封面图获取指南

封面图有两条路径,先选,再做。

| 路径 | 做法 | 适合场景 | 详见 |
| --- | --- | --- | --- |
| **A. 抓取现成图** | 抓 YouTube 缩略图、网页 OG 图、文档插图,或截视频帧 | 内容主角是一张本身就有视觉冲击力的现场画面(嘉宾正脸、产品截图、关键图表);或者文章是访谈 / 演讲 / 资讯转述 | 本文以下章节 |
| **B. HTML 模板生成** | 用极简纯白 + 厚重无衬线 + 一处渐变焦点的卡片模板,Chrome headless 出图 | 内容是观点 / 方法论 / 综述 / 解读,封面要直接传达文章主旨,而不是借现场画面;或者抓不到合适的现成图 | [cover-card-template.md](cover-card-template.md) |

**选路径 A 的判断**:你已经能在原视频 / 网页 / 文档里找到一帧"读者一看就懂这是什么"的画面。
**选路径 B 的判断**:封面要承担"文章一句话观点"的功能,而不是只显示来源。

如果不确定,先看视频缩略图或 OG 图——那张图本身已经能讲清楚文章是什么吗?能就走 A,不能就走 B。

---

## 路径 A — 抓取来源现成图

### YouTube 视频

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

### 网页文章

大多数文章页面有 Open Graph 图片，适合直接做封面：

```bash
# 用 curl 查看 og:image meta 标签
curl -s "ARTICLE_URL" | grep -i 'og:image'
```

如果 OG 图片质量不佳，用 Chrome DevTools MCP 截取文章首屏或文中核心图表。

---

### 本地文件

PDF / Markdown 通常没有配套图片,建议从文档内容中选取有代表性的图表截图,或根据文章主题自行准备封面图。如果文档里没有合适的图,直接走路径 B。

---

## 路径 B — HTML 模板生成原创卡片

详细规范、完整 HTML 模板、字段填法、渐变变体和截图命令,见 [cover-card-template.md](cover-card-template.md)。

一句话说明:

> 极简纯白底 + PingFang SC / Inter 700 字重 + 主标题可选橙紫渐变 + 一根 hairline 切分上下两层。Chrome headless 一行命令出 1800×766 的 2x 高清图,零依赖。


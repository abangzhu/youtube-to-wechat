# HTML 封面卡片模板

此模板是可调整的起点：白底、深色粗标题、少量辅助信息，适合以观点或问题为中心的文章。不是所有文章必须采用的品牌规范。路径选择和最终验收以 [cover-art-guide.md](cover-art-guide.md) 为准。

## 文案字段

| 字段 | 用途 |
| --- | --- |
| `article_title` | 已确认的文章 H1，供文件元信息和素材清单使用 |
| `cover_title` | 忠实于全文的封面短标题，允许有意分两行 |
| `kicker` | 可选的主题或真实来源，不编造公众号名、期号、权威身份 |
| `supporting_line` | 可选的必要补充，应能从正文追溯；编辑概括不冒充原话 |

优先保留核心标题，辅助信息放不下时可以删掉。直接引语需要准确来源，不能为了“金句”自行创造。标题长度、换行、字号一起调整，以阅读和裁切结果验收；不能修改已确认 H1 来迁就模板。

## 可直接保存的模板

替换占位字段并做 HTML 转义；用 `<br>` 设置有意换行时只插入可信标记，不直接把未转义的来源文本作为 HTML。保存到任务目录的 `cover.html`。

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{article_title}} · 封面</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; width: 900px; height: 383px; }
  body {
    background: #fff;
    color: #111;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
                 "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .card {
    width: 900px;
    height: 383px;
    padding: 40px 52px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .kicker { margin: 0; font-size: 18px; line-height: 1.3; color: #555; }
  h1 {
    margin: auto 0;
    font-size: 56px;
    line-height: 1.16;
    letter-spacing: -0.8px;
    font-weight: 750;
    overflow-wrap: anywhere;
  }
  .supporting {
    margin: 0;
    padding-top: 16px;
    border-top: 1px solid #ddd;
    font-size: 24px;
    line-height: 1.4;
    color: #333;
  }
  .accent { color: #a63716; }
</style>
</head>
<body>
<main class="card">
  <p class="kicker">{{kicker}}</p>
  <h1>{{cover_title}}</h1>
  <p class="supporting">{{supporting_line}}</p>
</main>
</body>
</html>
```

系统字体优先，无需下载陌生字体或为每次任务强制换字体。用户有字体、配色、品牌偏好时遵循其要求。可以给一个关键词加 `.accent`，也可以全黑；渐变、衬线或其他风格不是事实和阅读要求之外的禁区。空的可选元素应删除，避免留下无意义的行和留白。

## 渲染

优先用当前可用浏览器工具打开本地 HTML、设置画布尺寸、等待 `document.fonts.ready`（工具支持时）、截图卡片。调用参数按实际工具文档，不假定某一 MCP 名称或 screenshot 参数存在。

有本地 Chromium 且允许运行时，也可用 CLI。先确认实际可执行文件路径，使用隔离的临时 profile，不接管用户正在使用的浏览器：

```bash
# macOS 示例；其他系统替换为查到的可执行文件
COVER_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
COVER_PROFILE=$(mktemp -d)
"$COVER_BROWSER" --headless --hide-scrollbars \
  --user-data-dir="$COVER_PROFILE" \
  --force-device-scale-factor=2 --window-size=900,383 \
  --screenshot="/ABS/TASK/cover.png" \
  "file:///ABS/TASK/cover.html"
```

`/ABS/TASK` 必须替换为实际路径；含空格或特殊字符的本地 URL 需正确编码。临时 profile 仅在确认本次进程退出后清理；不要删除用户 profile。若系统权限限制启动浏览器，改用已提供的渲染工具，不能加禁用安全机制的参数绕过。

截图通常可按缩放因子输出更高分辨率，但仍需检查实际文件尺寸。需要 JPEG 时使用已安装的转换工具，例如：

```bash
# macOS
sips -s format jpeg cover.png --out cover.jpg
# 或已安装的 ffmpeg；确认目标是本任务派生文件后再覆盖
ffmpeg -i cover.png -frames:v 1 -q:v 2 cover.jpg
```

## 检查与调整

1. 看实际输出，确认占位符全部替换、字形正确、标题无裁切。用可用的布局读取检查 `scrollWidth > clientWidth` 或元素超出画布，作为辅助检查。
2. 按封面展示尺寸缩小预览，确认核心标题可读。两倍像素不会补救太小的相对字号。
3. 按可能使用的宽幅和方形裁切预览主体；若一张不能兼顾，按平台能力设置裁切或导出第二版。
4. 遇到溢出，先删无关辅助文案、精简 `cover_title` 或改换行，再适度调整字号、间距、布局。没有固定字数清零检查，也不把故意截掉文字称为设计。
5. 记录最终 `article_title`、`cover_title`、HTML 路径和图片在 `assets.json`。封面中的改写、数字和归属再次对照正文。

首次生成最终封面仍须满足主流程的标题与正文确认条件。后续用户明确要求改版时，沿用已确认内容继续修改，无需重新走标题选择。

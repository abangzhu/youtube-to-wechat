# 发布到 Notion（连文带图）

读取时机：成稿后，用户要求把 `article.md` 发布 / 上传到 Notion 知识库（如「放到 Notion 写作/AI/Blog 转载目录下」「连文带图创建一篇 Notion 文档」）。

用的是 Notion MCP 工具：`API-post-search`（找目录）、`API-post-page`（建页）、`API-patch-block-children`（灌正文）、`API-get-block-children`（验证）。

## 两条必须先知道的认知

**1. MCP 的 schema 是简化的，实际透传完整 Notion 块类型。**
`API-patch-block-children` 的入参 schema 只声明了 `paragraph` 和 `bulleted_list_item`，但实测 `heading_2`、`code`、`image`、`divider`，以及 rich_text 的 `annotations`（`bold` / `italic` / `color`）全都能正常透传创建。不要被 schema 限制住，放心传完整 Notion block JSON。

**2. 没有文件上传能力 —— 本地图片不能直接进 Notion。** 两条路：
- **来源是网页 / X / YouTube → 图片几乎都有公网 URL**（存在抓取保存的 `source.json` / `metadata.json` / 网页 og:image / X 的 `pbs.twimg.com` CDN）。用 **external image block** 直接引用公网 URL，最省事，也保证图文位置精确对应。代价：图归原站托管，原站删图则 Notion 里失效；要永久副本得让用户在 Notion 桌面端手动拖入本地图替换。
- **没有公网 URL（纯本地截图）→** 文字正文先发，图片位置留 `[图：文件名]` 占位 paragraph，让用户手动拖入。不要假装能自动上传。

## 流程

**0. 定位目录（别发错地方）**
`API-post-search` 搜目录名 → 取候选 page_id → 对命中的页 `API-retrieve-a-page` 逐级验证 parent 链（确认它真在「写作 → AI → Blog转载」这条链下，而不是同名的另一个目录）。

**1. 建页**
`API-post-page`，`parent = {"page_id": "<目录id>"}`，`properties.title` 放文章主标题。
注意：**`article.md` 第一行的 H1 是 Notion 的 page title，不作为正文 block 重复**。可给一个 `icon` emoji。

**2. 灌正文（分批）**
`API-patch-block-children` 按章节分批追加。限制：单次 ≤ 100 个 block；单个 rich_text `content` ≤ 2000 字符。每批一个或几个 H2 章节，按原文顺序。

**3. 验证**
`API-get-block-children` 数一下块 / 图数量，或直接打开返回的页面 URL 看一眼图片是否都渲染出来（external 图偶有不显示，需提示用户）。

## 图片映射陷阱（最容易错）

抓取脚本下载的本地文件名顺序（`img-01.jpg`、`img-02.png`…）**经常和 `source.json` 里 media 数组的顺序不一致**（典型症状：本地 png 在 img-02/04，但 media 数组里 png 在末尾）。**绝不要按 media 数组下标硬配 img-01..N。**

正确做法：`article.md` 的图片 alt 里带了 media ID（`![image 2061854734441725952](.../img-02.png)`）。用这个 ID 去匹配 `source.json` 里每个 entity 的 `media_id`，建立精确的「本地文件名 → 公网 URL」映射。脚本示例：

```python
import json, re
d = json.load(open("<source.json>"))
art = d["tweet"]["article"]                       # X article 的结构，其他来源相应调整
id2url = {art["cover_media"]["media_id"]: art["cover_media"]["media_info"]["original_img_url"]}
for m in art["media_entities"]:
    id2url[m["media_id"]] = m["media_info"]["original_img_url"]
# article.md 里 alt 的数字就是 media_id，按正文顺序取 URL
for alt, fn in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', open("<article.md>").read()):
    mid = alt.replace("image", "").strip()
    print(fn.split('/')[-1], "->", id2url.get(mid, "cover" ))
```

## 块构造速查（Notion block JSON）

```jsonc
// 段落
{"type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"..."}}]}}
// 章节标题
{"type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"..."}}]}}
// 加粗小标题（对应正文里的 **加粗** 段，如模式名）
{"type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"..."},"annotations":{"bold":true}}]}}
// 列表项，首词加粗（对应 "- **X** 说明"）
{"type":"bulleted_list_item","bulleted_list_item":{"rich_text":[
  {"type":"text","text":{"content":"X"},"annotations":{"bold":true}},
  {"type":"text","text":{"content":" 说明……"}}]}}
// 代码块（英文 prompt + 中文译文同块，用 \n 换行）
{"type":"code","code":{"language":"plain text","rich_text":[{"type":"text","text":{"content":"英文...\n\n中文..."}}]}}
// 外链图片
{"type":"image","image":{"type":"external","external":{"url":"https://..."}}}
// 分隔线
{"type":"divider","divider":{}}
// 来源行（灰色斜体注记）
{"type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"内容来源，..."},"annotations":{"italic":true,"color":"gray"}}]}}
```

## 标点
正文沿用中文全角即可。来源行 URL 和英文标题里的半角冒号（`X: Y`、`https:`）保留，不要全角化。

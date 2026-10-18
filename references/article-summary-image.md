# 文章摘要图：先保证手机可读

摘要图是可选正文素材。只有一张图能帮助读者理解方法步骤、层级或比较关系时才制作；不把每篇文章都改成流程图，也不在图里堆完全文。先准备结构草案，用户确认标题与正文后再生成最终图。

## 内容与布局

选一个关系作为主轴，通常保留 3–6 个短节点或少量可比较项目。数量只是设计起点，不是内容规则。节点文案来自定稿，保留影响含义的限定条件；图里的数字、箭头和因果与正文一致，不能因为排版方便制造必然顺序或虚构收益。

用与主题相符的视觉结构：步骤用纵向流程，层级用分组，比较用少量并列项。手机上的三列细字通常不如纵向条目清楚。图需要很多解释才能看懂时，先删减或拆分；如果简洁文字已经足够，可以不做图。

## 尺寸与可读性

按 **360–430 CSS 像素的实际显示宽度**设计和预览。建议以约 390px 宽的布局起稿、正文 16–18px、标签至少约 14px，再用 2× 或 3× 像素输出清晰图片；这些是起点，实际看图决定是否需要更大字。

大画布也可以使用，但要计算缩小后的效果：1200px 宽图中的 20px 字，显示在 390px 宽时只剩约 6.5px；增加截图像素密度不会改善这个比例。完整截图缩到 360px 后仍应能直接阅读核心内容，无需放大。

系统中文字体或用户指定字体即可。不强制每次换字体，不依赖未安装的英文展示字体，也不把某个颜色或 serif/sans-serif 当作普遍禁令。保证字形完整、对比清楚和层级一致。

## 可用 HTML 起点

以下模板按手机宽度纵向排列。替换为文章的真实结构；示例只有三个节点，可增减，不必凑满。字段要 HTML 转义，空元素删除。

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{article_title}} · 摘要</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body {
    color: #18201c;
    background: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
                 "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .summary {
    width: 100%;
    max-width: 430px;
    padding: 26px 22px;
    background: #f7f8f4;
  }
  h1 { margin: 0 0 12px; font-size: 28px; line-height: 1.25; }
  .intro { margin: 0 0 22px; font-size: 17px; line-height: 1.55; }
  ol { list-style: none; margin: 0; padding: 0; }
  li { display: flex; align-items: flex-start; gap: 12px; padding: 17px 0; border-top: 1px solid #ccd2c8; }
  .number { flex: 0 0 26px; padding-top: 3px; font-size: 15px; font-weight: 700; color: #3a6047; }
  .step { min-width: 0; }
  h2 { margin: 0 0 6px; font-size: 20px; line-height: 1.35; }
  .step p, .limit { margin: 0; font-size: 16px; line-height: 1.6; overflow-wrap: anywhere; }
  .limit { margin-top: 22px; padding-top: 16px; border-top: 2px solid #3a6047; }
</style>
</head>
<body>
<main class="summary">
  <h1>{{summary_title}}</h1>
  <p class="intro">{{one_sentence_relationship}}</p>
  <ol>
    <li><span class="number">01</span><div class="step"><h2>{{step_1_title}}</h2><p>{{step_1_text}}</p></div></li>
    <li><span class="number">02</span><div class="step"><h2>{{step_2_title}}</h2><p>{{step_2_text}}</p></div></li>
    <li><span class="number">03</span><div class="step"><h2>{{step_3_title}}</h2><p>{{step_3_text}}</p></div></li>
  </ol>
  <p class="limit">{{necessary_limitation_or_takeaway}}</p>
</main>
</body>
</html>
```

无需固定高度，按内容自然延展。若主题是比较或层级，应调整结构与序号，不能让模板反过来改变原意。顶部不必重复来源履历和长文章标题；必要署名或图表出处可保留，不能因为追求极简删掉归属。

## 渲染与验收

1. 保存 `summary.html`，用当前支持的浏览器/渲染工具打开，检查真实字体加载后截图 `.summary` 元素或页面内容。工具用法见 [tool-adapters.md](tool-adapters.md)。
2. 分别在 360px 和 430px viewport 检查无横向溢出；长词、数字和中英混排都不能出框。再按约 390px 宽输出高密度 `summary.png`。
3. 实际查看最终文件缩到手机宽度的效果，核对每个标签、数字、箭头和限定条件，不把 DOM 无溢出当作可读性证明。若字太小，减少内容或调整布局；不能仅提高导出分辨率。
4. 登记 [assets.json](visual-capture.md#3-assetsjson-契约)：`role: "summary"`、HTML 源路径、图片路径、描述性 alt、正文锚点和核验结果。不要假设平台会自动上传本地图。

## 插入正文

根据阅读顺序放在标题后或解释该关系的段落后，不强制占据文章顶部。图应独立易读；必要的单位、来源、适用条件可以配简短图注，不能为了“让图自己说话”省掉理解必需的信息。

```markdown
# 用户确认的文章标题

![评测流程：记录失败、校准标准、比较改动，并保留回归测试](summary.png)

正文……
```

摘要图、原视频证据图和封面承担不同作用，可以按需要并用，也可以只做其中一类。正文的结构图不能替代原始证据核验，封面也不必重复摘要图的信息密度。

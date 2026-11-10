# 《评测分数上涨，为什么上线效果没变？》封面设计说明

本次交付为设计方案与可直接使用的图像生成提示词；标题与正文已确认。本轮未生成图片，尚未进行成图验收。

## 设计方案

- **正式文章标题（article_title）**：评测分数上涨，为什么上线效果没变？
- **封面文案（cover_title）**：评测分数上涨，为什么上线效果没变？
- **画幅**：仅制作约 2.35:1 的宽幅封面，建议按 2350×1000 的构图规划。生成工具的实际输出尺寸需另行核验。
- **路径与风格**：原创编辑插画。采用简洁的几何拼贴、细腻的印刷质感和少量柔和阴影，体现理性的技术议题。
- **配色**：浅冷灰底色 #EEF1F5，深冷灰文字 #27313F，钴蓝强调色 #2455D6，中冷灰辅助元素 #AAB4C2。钴蓝只用于标题重点和插画关键部位，避免整张画面过度饱和。

标题放在画面左侧约 55% 区域，分为两行：“评测分数上涨，”与“为什么上线效果没变？”。使用粗体中文无衬线字体；“评测分数上涨”用钴蓝，其余文字用深冷灰。完整保留逗号和问号，不另加副标题、身份引题或宣传语。

右侧约 45% 为一个完整的视觉比喻：一块透明的窄小“评测观察框”中，是几张形状完全相同的钴蓝样本卡片；卡片向上错落叠放，暗示在局部评测中不断提高的成绩。观察框外延伸着一条平直的业务流程带，上面分布着大小、轮廓各不相同的冷灰与少量钴蓝任务块；观察框中的单一样本只对应外部任务的一小部分。用同一组图形的“框内重复、框外多样”表达评测过拟合与代表性样本不足的问题，用平直的流程带呼应标题中的上线效果疑问。

这一构图是概念插画，不是实验结果或真实业务仪表盘。流程带的平直仅作视觉隐喻，不能配坐标、刻度或数值，也不声称正文证明了所有上线问题都由评测过拟合造成。画面不使用故障、停摆或崩溃符号，以免把“效果没变”夸大成“上线失败”。

左右保留约 6% 安全边距，上下留出足够呼吸空间。标题与插画之间保持清楚间隔，细节服从手机缩略图阅读。本方案专为宽幅布局，完整标题不适合直接居中方裁；本轮不增加方形版本。

## 可直接使用的图像生成提示词

```text
Create ONE finished original editorial illustration cover for a Chinese WeChat article. Very wide horizontal composition, approximately 2.35:1 aspect ratio; plan the layout on a 2350 × 1000 canvas. Produce only the wide cover, not a square version or a mockup.

Article topic: evaluation scores improve, but the improvement may not carry over to real-world business outcomes. The article discusses evaluation overfitting, representative samples, and actual business results. It provides no quantified business gains. Treat every visual element as a conceptual metaphor, never as a real experiment, measured chart, or product screenshot.

Brand palette: light COOL GRAY background #EEF1F5, dark COOL GRAY typography #27313F, COBALT BLUE accent #2455D6, medium COOL GRAY supporting shapes #AAB4C2. Keep all colors cool. Use no terracotta, orange, warm ivory, or neon colors. Restrained editorial print texture, crisp geometric paper-cut shapes, subtle soft shadows, intelligent and calm magazine art direction.

Typography occupies approximately the left 55% of the image. Render ONLY the following exact Chinese text, arranged in exactly two lines:
Line 1: 评测分数上涨，
Line 2: 为什么上线效果没变？

The exact full title is: 评测分数上涨，为什么上线效果没变？
Preserve every Chinese character, the Chinese comma, and the question mark. The question mark is essential. Do not turn the question into a statement. Use very large, bold, clean Chinese sans-serif typography, clearly readable in a small mobile thumbnail. Make the words “评测分数上涨” cobalt blue; use dark cool gray for all remaining characters and punctuation. Keep the title comfortably inside safe margins. Add no other words, labels, subtitles, captions, numbers, quotations, signatures, logos, or watermarks.

The right approximately 45% contains ONE coherent editorial illustration. Show a small, narrow, translucent rectangular evaluation viewing frame. Inside it, several identical cobalt-blue rounded rectangular sample cards repeat the same simple abstract motif. Stack these identical cards at progressively higher positions, suggesting improvement within a narrow evaluation setting. Do not draw chart axes, tick marks, percentages, scores, data labels, or a quantitative graph.

Around and beyond this small frame, a broad, flat horizontal workflow ribbon extends through a varied set of abstract task blocks. The task blocks have visibly different sizes and silhouettes: rounded rectangles, circles, and irregular polygonal shapes. Most are cool gray; only a few are cobalt blue. Make it visually clear that the identical samples inside the small frame represent only a small subset of the diverse tasks outside it. The rising arrangement of repeated samples and the flat workflow ribbon should form a subtle visual tension, expressing the article's question about evaluation gains failing to translate into visible business improvement. The ribbon is an abstract conceptual device, not a time series or measured business performance line.

Keep the external workflow intact and calm: no broken machinery, stop signs, error messages, crashes, disaster symbols, or depictions of business collapse. Do not imply guaranteed business gains or invent numerical benefits. No human portraits, endorsements, official marks, robots, chips, glowing brains, code rain, or generic science-fiction imagery.

Maintain generous negative space between the title and the illustration. Keep important content approximately 6% away from the left and right edges and comfortably away from the top and bottom. The title must remain dominant; simplify illustration details so the inside-versus-outside sample relationship remains legible at thumbnail size. The final composition should feel like a carefully art-directed original editorial cover, with crisp Chinese typography and a distinctive cool-gray and cobalt-blue identity.
```

## 后续成图验收

实际生成后，打开原图逐字核对标题、逗号与问号，检查缺字、乱码和边缘截断；缩小至约 470×200 预览，确认两行标题可读、框内单一样本与框外多样任务仍能区分。核验实际宽高比接近 2.35:1，画面没有额外数字或效果承诺。若中文排字不准确，保留插画，以可控排版方式重新叠加同一标题。

最终位图生成后再保存原始输出、cover.jpg 与 cover-prompt.txt，并登记素材路径、标题、生成出处和核验结果；当前方案不冒充已生成或已验收的封面。

# 视觉证据与素材清单

现场演示先提炼结论，再判断是否需要原视频截图。文字难懂时先改写，不用配图补救操作回放。截图、封面和摘要图统一登记在本文件定义的 `assets.json` 中。

## 1. 什么值得配图

先写清发现、关键证据、原因和意义，再问图片增加了什么：关键数据、结构关系、方案差异或产品外观值得保留；一行标题、模糊白板和只有跟随点击过程才能理解的界面通常不需要。讲者说“看这里”只用于寻找候选画面，不是强制插图信号。

不设默认图片数量。解释型公众号可以无图；可复现教程在操作确实依赖界面时配步骤图。代码需要复制时优先用代码块；不要把不可读的终端小字截图当作代码交付。

草稿可以留 `[图:MM:SS - 待核对的关键内容]`，但定稿必须替换、删除或明确列为未完成项。没有时间戳时可从原生转录面板按关键词定位，或补取带时间戳来源；不能按文字长度估算后假装是准确帧。

## 2. 获取视频画面

按当前浏览器工具文档调用，工具名、页面 ID、元素定位方式和文件输出路径都以实际 schema 为准。不假定 `take_screenshot` 必然支持某个 `uid`、所有浏览器都支持任意 JS，或网页会一直保留相同 DOM。

1. 打开正确视频，核对 URL、标题和时长。先确认当前播放的是正片；广告、直播回放与正片的时间轴可能不同。
2. 由转录时间戳换算目标秒数，跳转并暂停。若工具支持页面 JS，可使用下面的 DOM 操作；否则使用播放器控制。
3. 等 seek 完成、目标帧可解码，再重新读取时间和播放器状态。获取元素定位或边界框，优先截图视频区域。
4. 保存到任务目录，实际查看图片，确认对应的标题、标签、数字或结构。一次截图成功不代表其他时间点自动正确。

可选 DOM 示例，目标值按实际时间修改：

```javascript
async () => {
  const v = document.querySelector('video');
  const targetSeconds = 141;
  if (!v || !Number.isFinite(v.duration)) {
    return { error: '视频尚未可定位，先检查加载状态和正片' };
  }
  if (targetSeconds < 0 || targetSeconds >= v.duration) {
    return { error: '目标时间超出当前视频范围' };
  }
  v.pause();
  const seekResult = await new Promise(resolve => {
    let timer;
    const finish = result => {
      clearTimeout(timer);
      v.removeEventListener('seeked', onSeeked);
      resolve(result);
    };
    const onSeeked = () => finish('seeked');
    v.addEventListener('seeked', onSeeked);
    timer = setTimeout(() => finish('timeout'), 8000);
    if (Math.abs(v.currentTime - targetSeconds) < 0.05 && !v.seeking) {
      finish('already-positioned');
    } else {
      v.currentTime = targetSeconds;
    }
  });
  v.pause();
  return {
    url: location.href, title: document.title, seekResult,
    currentTime: v.currentTime, duration: v.duration,
    seeking: v.seeking, readyState: v.readyState,
    videoWidth: v.videoWidth, videoHeight: v.videoHeight
  };
}
```

`timeout`、`seeking: true` 或 `readyState < 2` 时先检查状态，不立即截图。即使数值正常也需实际看图；字幕时间常对应一句话，图表可能在前后几秒才稳定显示。

### 元素截图不可用时

使用受支持的 viewport 截图，再按当时的视频边界裁切。边界可从工具定位能力或允许的 DOM 查询获得：

```javascript
() => {
  const v = document.querySelector('video');
  if (!v) return null;
  const r = v.getBoundingClientRect();
  return {
    left: r.left, top: r.top, width: r.width, height: r.height,
    viewportWidth: innerWidth, viewportHeight: innerHeight,
    devicePixelRatio
  };
}
```

先确认视频完全位于截图范围。**不要直接假设截图像素比等于 DPR**：工具可能输出 CSS 像素。用实际截图宽高与 viewport 宽高计算缩放，检查两个方向一致，再将边界换算为图像像素。若截图带浏览器边框、整页滚动或不同坐标系，重新选受支持的截图方式。

例如核对后的视频区域确为 `1572×884`、左上角为 `(32,136)` 时：

```bash
ffmpeg -i viewport.png -vf "crop=1572:884:32:136" -frames:v 1 frame.jpg
```

裁切不能删除会改变解释的图例、坐标、单位和样本量。文件尺寸、哈希或平均色只能检查损坏、重复等问题，不能证明画面内容正确。若预览疑似缓存，重新读取实际文件或换受支持的预览工具；仍无法看清就不要把该图记为已核验。

同一视频可复用标签页批量截图，但每个时间点重新确认正片、时间和关键内容；页面重排后重新获取元素或边界。工具故障只记录当时环境，不把旧故障解释为所有版本的永久缺陷。

## 3. `assets.json` 契约

这是本技能素材映射的唯一权威定义。每个正文图片、封面或摘要图一条记录，路径相对任务目录、指向真实文件。`id` 为稳定唯一标识；**alt 是描述，不是 ID 容器**。

```json
{
  "version": 1,
  "assets": [
    {
      "id": "eval-comparison",
      "role": "body",
      "local_path": "VIDEO_ID-frame-10620.jpg",
      "source_url": null,
      "source_page_url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "source_timestamp": 6380,
      "alt": "实验对比：行动建议通过 48/48，忠实度通过 3/48",
      "placement": {
        "article": "article.md",
        "relation": "after",
        "anchor": "填写图片前一段的唯一完整原文，用于定位"
      },
      "verification": {
        "status": "pending",
        "notes": "待实际看图核对列标题、两项分母和样本条件"
      }
    }
  ]
}
```

字段规则：

- 必须有 `id`、`role`、`local_path`、`source_url`、`source_timestamp`、`alt`、`placement`。`role` 为 `body`、`cover` 或 `summary`。
- `source_url` 只放能取得**这张图片**的直接 URL，没有则为 `null`。视频页、文章页等出处另放 `source_page_url`，不能当 external image URL。原始图片若经裁切，需额外记录 `transform`，远端发布使用与成稿一致的版本。
- `source_timestamp` 用视频秒数，非视频素材为 `null`。不能从文件名猜秒数。
- `placement.relation` 为 `before`、`after` 或 `cover`；正文用唯一段落原文作 `anchor`，摘要可以定位到确认后的 H1。封面使用 `relation: "cover"`、`anchor: null`。编辑锚点文字后同步更新，不依赖会漂移的行号。
- `verification.status` 为 `verified` 或 `pending`。记录核对了哪些内容；截图时间正确不足以设为 `verified`。
- 原创 HTML 素材可增加 `generated_from` 指向 HTML 源；其 `source_url` 和 `source_timestamp` 为 `null`。封面另记 `article_title` 与 `cover_title`，见封面指南。

Markdown 根据相对路径精确映射清单：

```markdown
![实验对比：行动建议通过 48/48，忠实度通过 3/48](VIDEO_ID-frame-10620.jpg)
```

不要按文件数组顺序、alt 数字或文件名近似值配图。解析路径时保留目录、URL 解码并规范化；校验其仍在任务目录内。每个 Markdown 图片必须唯一匹配清单，缺失或冲突就停止该图发布，不能默认换成封面。

## 4. 图文与平台验收

先给读者结论，再将图放在相关段落之后。alt 描述图中真正可见的关系，不加入图外结论；正文仍需说明重要判断和边界。来源文字很小、在手机上看不清时，可裁到关键区域或依据已核实数据重绘，并标明为整理图。

本地 Markdown 能显示图片不等于发布平台已上传。公众号、Notion 等平台是否自动上传本地图，必须按实际编辑器或连接器验证；交付本地包时说明图片仍在包中。上传映射和恢复流程见 [publish-to-notion.md](publish-to-notion.md)。

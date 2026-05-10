# youtube-to-wechat

把任意来源的内容变成一篇可发布的微信公众号文章——一个 Claude Code / Cursor / 其他 agent 可加载的 Skill。

支持来源：

- YouTube 视频（自动抓字幕 + 双语对照）
- 网页文章
- 本地文档（PDF / Markdown / TXT）

产出：一篇可直接粘贴进公众号后台的中文长文，包含标题候选、章节结构和封面图提示。

---

## 安装

通过 [`skills`](https://github.com/vercel-labs/skills) 管理器一键安装到你的 Claude Code：

```bash
# 全局安装（~/.claude/skills/youtube-to-wechat/）
npx skills add abangzhu/youtube-to-wechat -g

# 或只装到当前项目（.claude/skills/youtube-to-wechat/）
npx skills add abangzhu/youtube-to-wechat
```

卸载：

```bash
npx skills remove youtube-to-wechat -g
```

> ⚠️ **不要**在本仓库目录内跑 `npx skills add ./ -g`：`skills` CLI 会把源目录替换成指向安装目标的 symlink，导致源文件丢失。要本地自测请 `cd` 到仓库之外的目录再执行。

---

## 触发方式

安装后，对着 Claude 说任意一句：

- 「帮我把这个 YouTube 视频写成公众号文章：<URL>」
- 「这篇英文文章翻译整理成一篇中文长文」
- 「读一下这个 PDF，按我的风格写成稿子」

Claude 会自动调用这个 skill 走完 8 步流程。

---

## 工作流概览

1. 获取并整理内容，生成原始转录和工作底稿
2. 调查人物 / 作者背景
3. 从主播或作者视角 + 读者视角分析内容
4. 写公众号初稿
5. 对照原文查漏
6. 用读者、编辑、事实三层视角评估
7. 根据评估重写
8. 拟标题、加章节标题、准备封面图

---

## 目录结构

```
youtube-to-wechat/
├── SKILL.md                            # 主流程（给 agent 读）
├── references/
│   ├── translation-quality.md          # 英译中质量规则
│   ├── wechat-writing-rules.md         # 公众号成文规则
│   ├── cover-art-guide.md              # 封面图生成规则
│   └── youtube-transcript-fallback.md  # 字幕抓取兜底方案
├── scripts/
│   └── parse_vtt.py                    # VTT 字幕解析脚本
└── evals/
    └── evals.json                      # 回归测试样例
```

---

## 依赖

- `yt-dlp`（抓 YouTube 字幕）
- Python 3（跑 `parse_vtt.py`）
- 可选：`ffmpeg`（处理音频兜底）

---

## License

MIT

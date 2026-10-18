# 报告交付工作坊记录

这是一份合成教学材料，用于练习将现场记录改写成文章或教程。以下代码只模拟报告交付工具，不调用模型或外部服务。

[00:00] 环境是 Python 3.10 或更新版本。模型收到的任务模板只有“请写一份报告”，没有指定将报告作为文本返回还是保存成文件。演示环境禁止写文件。

[00:30] 讲者打开运行记录，选中写作回合，展开工具调用。预先记录的 16 个写作回合中有 13 个尝试调用保存文件工具。这是尝试次数；记录没有给出 13 次均失败的统计。

[01:00] 讲者切换到终端，展示一条 PermissionError，再切回调用树。该条记录的 delivery 参数为 file。

[01:20] 为了复现交付工具的行为，把下面内容保存为 demo.py：

```python
def finish_report(report, delivery):
    if delivery == "file":
        raise PermissionError("File writes are not allowed")
    return report

print(finish_report("Example report", "file"))
```

[02:00] 在终端运行 python3 demo.py，输出 PermissionError: File writes are not allowed。讲者放大窗口并再次运行，错误相同。

[02:30] 将最后一行的 delivery 参数从 file 改成 text，重新运行后输出 Example report。

[03:00] 讲者把 Agent 的任务模板补成“请写一份报告，直接返回报告文本，不调用保存文件工具”。材料没有提供修改后全部样本的成功率。

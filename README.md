# Python `marshal` 模块稳定性与正确性测试套件

本仓库用于验证 Python `marshal` 模块在以下方面的行为：

- 正确性：`dump`/`dumps` 与 `load`/`loads` 的往返是否保持语义一致
- 稳定性：相同输入在同一 Python 版本内是否产生 hash-identical 的字节流
- 鲁棒性：对非法输入、截断字节流、超大对象和不支持类型的处理是否合理
- 可移植调查：在不同操作系统与 Python 版本下采集结果并比较差异

## 目录结构

- `tests/`：基于 `unittest` 的测试套件
- `scripts/collect_marshal_digests.py`：输出当前环境下的摘要结果，便于跨平台/跨版本比较
- `.github/workflows/ci.yml`：Windows / Linux / macOS 与 Python 3.11-3.13 测试矩阵
- `report/report.md`：最终报告草稿

## 本地运行

```bash
python -m unittest discover -s tests -v
python scripts/collect_marshal_digests.py
```

## 测试策略概览

- 黑盒：等价类划分、边界值分析、错误推测、随机模糊测试
- 白盒：依据 `marshal.c` 中的类型分派、引用跟踪、递归深度和错误分支设计针对性测试
- 跨进程稳定性：通过不同 `PYTHONHASHSEED` 重启独立解释器，验证同一输入字节流是否保持一致

## 说明

- `marshal` 官方文档明确说明格式可能随 Python 版本变化，因此本仓库不把跨版本字节完全一致设为必须通过的断言。
- 当前仓库的自动化验证目标为 Python 3.11-3.13；更旧版本可作为扩展调查对象，但不在当前提交的受支持自动化范围内。
- 当前公开仓库地址：`https://github.com/cccbbbaaa666/marshal-stability-suite`

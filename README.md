# 图片型 PDF（试卷）一站式处理

## 流程图

```mermaid
sequenceDiagram
    PDF->>Json: OCR
    Json->>questions: GPT
    questions->>answers: GPT
```

## 用途

该工具有效解决了部分 PDF 被水印席卷而观感差，或因无法直接选中文字而工作低效等问题。

## 使用

见代码
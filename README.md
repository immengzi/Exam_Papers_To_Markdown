#  照片型试题自动生成参考答案

## 用途

解决照片型试卷无法通过简单的 OCR 识别结构化内容的问题

## 准备

1. 百度云 OCR API（有免费额度）
2. OpenAI API（自行获取）

## 流程图

```mermaid
sequenceDiagram
    PDF->>Json: OCR
    Json->>questions: GPT
    questions->>answers: GPT
```

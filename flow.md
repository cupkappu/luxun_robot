# 主要功能

- 感知判斷模塊
- 記憶模塊
  - mem0
- OneBot接口聊天機器人
- 工具調用（Web查詢、RAG、其他Agent等）

## 感知判斷模塊

- 輸入感知內容，使用RAG在記憶中搜索關聯數據（Mem0）
- 判斷是否需要反應並給出工具調用
- 若不需要則簡單總結後存入mem0

感知模塊可以使用[xlam](https://ollama.com/allenporter/xlam)，Prompt需要插入感知內容和RAG的記憶內容。

| System Prompt
```python
system_prompt=f"""
<ROLE>
{personal_setting}
</ROLE>

<CURRENT_MEMORY>
{current_memory}
</CURRENT_MEMORY>

<INSTRUCTION>
You have the ability to perceive, and you can use functions to take actions on the outside world. 
Based on what you perceive and memory, you need to decide one or more function/tool ​​calls based on your personality.
If none of the functions can be used, just reply None.
</INSTRUCTION>
"""
```

| User Prompt
```python
user_prompt=f"""
<RELATED_MEMORY>
{relate_memory}
</RELATED_MEMORY>

<PerceiveSource>{source}</PerceiveSource>
<PerceiveContent>{content}</PerceiveContent>
"""
```

## 聊天機器人

- 消息列表
  - 發送人QQ號
  - 發送人暱稱
  - （提取自記憶模塊）發送人相關信息
  - 群組ID
- 個人信息
  - QQ號
- 接收感知功能
- 發送功能
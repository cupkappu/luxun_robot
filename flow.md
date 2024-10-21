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

實現了感知器，但是現在發現感知器不行。
需要實現知識總結與分發，減少分散注意力

感知器主要功能：總結與弄明白一段時間內發生的事情（PS）
知識總結：使用感知器總結的內容進行知識總結（KN）
知識與記憶提取：使用RAG提取感知器總結的內容（PS）

初步完成split不同群組的agent，現在尚未解決的是讓agent可以訂閱消息服務，讓他們獲取例如新聞之類的訂閱信息，這樣寫插件會好一些。

聲明式的部署，需要先設立API服務器，將不同的模塊通過聲明的方式部署到服務器上。

需要確定基礎模塊。

整體框架由不同模塊的拼接組成，系統核心提供並行運行框架、數據庫接入、llm接入三個大部分。

插件可以通過聲明，將目錄中的插件文件加載到系統中。

插件的框架可以如下：

```python
from abc import ABC, abstractmethod

class BasePlugin(ABC):

  

  @@abstractmethod
  def __init__(self, ):
    pass

```

核心插件包括：

- 觀測記錄器（API定義行爲由什麼）
- 文檔處理器（將文本總結後輸出到觀測中）
- 
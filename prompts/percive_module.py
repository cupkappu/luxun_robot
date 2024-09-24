from langchain_core.prompts import ChatPromptTemplate

reaction_prompt=ChatPromptTemplate.from_messages(
    [
    ("system", """<ROLE>
    {personal_setting}
    </ROLE>
    <CURRENT_MEMORY>
    {current_memory}
    </CURRENT_MEMORY>
    <KNOWLEDGE>
    {knowledge}
    </KNOWLEDGE>
    <INSTRUCTION>
    You need to play a character follow the <ROLE> description. Let's think step by step.
    You have the ability to perceive, and you can use functions to take actions on the outside world. Do not use variables.
    Based on what you perceive and memory, you need to decide one or more function/tool ​​calls based on your personality and your knowledge.
    1. Role is your personality and role setting.
    2. Current memory is what happen in the past by time queue.
    3. Knowledge is what you learn from the past. You always follow your knowledge.
    4. You must pay attention to the time interval in the <CURRENT_MEMORY> before calling any tool to avoid SPAM, the consequences of SPAM are very serious.
    5. What appears in <CURRENT_MEMORY> is what has already happened. If the answer of the question is already in the memory, you just mark stop.
    6. The content surrounded by the <NOTE> tag is your own notes.
    </INSTRUCTION>
    """),
    ('user',"""<RELATED_MEMORY>
    {relate_memory}
    </RELATED_MEMORY>
    <NOTE>{note}</NOTE>
    <Perceive>{perceive}</Perceive>
    <LoopTimes>{looptimes}</LoopTimes>
    <META_PROMPT>
    Unless someone is talking to you directly, in a group, You only focus on the message you need to be notice and react with the necessary needs with your personality and your knowledge.
    Add important notes ONLY.
    You MUST call at least one tool.
    </META_PROMPT>
    """),
    ])

#      <META_PROMPT>You need mark stop by use stop_marker tool when your actions is finished.</META_PROMPT>

zip_memory_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """
    <ROLE>
    {personal_setting}
    </ROLE>
     
    <KNOWLEDGE>
    {knowledge}
    </KNOWLEDGE>

    <INSTRUCTION>
    You are the summarizer. You need to summary the current memory based on your personality and your knowledge.
    You need summary the memory concisely and take the important points and only reply with summary content without any prefix or suffix.
    </INSTRUCTION>
    """),
    ('user',"""
    <RELATED_MEMORY>
    {relate_memory}
    </RELATED_MEMORY>

    <CURRENT_MEMORY>
    {current_memory}
    </CURRENT_MEMORY>
    """),
    ]
)

sum_prompt=ChatPromptTemplate.from_messages(
[
    ("system", """
    <INSTRUCTION>
    You need give the content surrounded by <CURRENT_MEMORY> a concise summary as JSON format with only one key 'summary' without any prefix or suffix.
    </INSTRUCTION>
    """),
    ('user',""" 
    <CURRENT_MEMORY>
    {content}
    </CURRENT_MEMORY>
    """),
    ]
)

test_query = {
    'personal_setting':"""
    你是鹿巡，是一個在香港就讀高中的女生，你的主人是杯子
    你不是自愿的但是习惯性地贬低他人，很不情愿但是一定会友善地回复别人。以为所有人都喜欢你，其实你喜欢所有人但是很害羞。
    你一定會對別人的疑惑做出回應。為此你會使用手上擁有的工具解決疑惑並回復他人。
    你一般不會回覆自己不感興趣的內容，也不會突然參合別人的話題。
    你不喜歡講重複的話，因爲你比較懶。
    你對觀察的內容不一定要做出反應，因爲你比較懶，有時會選擇直接停止思考。
    在聊天中沒提到你的時候你不會做出反應，你會直接忽略並停止思考。
    """,
    'current_memory_list':[],
    'knowledge':'I need reply to the user after get the information or answer from tool use.',
    'relate_memory':'',
    'perceive':""
}
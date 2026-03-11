import streamlit as st
import requests

# 页面基础配置，必须放在最前面
st.set_page_config(
    page_title="代码学习智能审查助手",
    page_icon="💻",
    layout="wide"
)

# 后端接口地址，本地开发用这个，部署后替换成线上地址
BACKEND_BASE_URL = "http://127.0.0.1:8000"

# 页面标题
st.title("💻 代码学习智能审查助手")
st.caption("基于RAG与大模型的编程答疑系统 | 代码智能分析 · 编程问题答疑")

# ========== 第一部分：代码分析功能 ==========
st.divider()
st.header("🔍 代码智能分析")
# 页面分栏布局：左边代码输入，右边结果展示
col_code, col_result = st.columns([1, 1])

# 左侧：代码输入区
with col_code:
    st.subheader("📝 代码输入区")
    # 编程语言选择下拉框
    language = st.selectbox(
        "选择代码对应的编程语言",
        options=["Python", "Java", "C++", "JavaScript", "Go"],
        index=0,
        key="code_language"
    )
    # 代码输入框，全版本兼容
    code_content = st.text_area(
        "请粘贴你要分析的代码",
        height=300,
        placeholder="在这里输入你的代码...",
        key="code_input"
    )
    # 功能按钮
    analyze_btn = st.button(
        "开始分析代码",
        type="primary",
        use_container_width=True,
        key="analyze_btn"
    )

# 右侧：结果展示区
with col_result:
    st.subheader("📊 分析结果")
    analyze_result_box = st.container(height=350, border=True)
    # 初始提示
    with analyze_result_box:
        st.info("请输入代码，点击「开始分析代码」查看结果")

# 代码分析按钮点击逻辑
if analyze_btn:
    # 入参校验
    if not code_content.strip():
        st.toast("请先输入要分析的代码！", icon="⚠️")
    else:
        # 调用后端接口，显示加载动画
        with st.spinner("正在分析代码，请稍候..."):
            try:
                # 发送POST请求到后端接口
                response = requests.post(
                    url=f"{BACKEND_BASE_URL}/api/code-analysis",
                    json={
                        "code": code_content,
                        "language": language
                    },
                    timeout=60
                )
                # 处理接口返回结果
                if response.status_code == 200:
                    result_data = response.json()["data"]
                    with analyze_result_box:
                        st.markdown(result_data)
                    st.toast("代码分析完成！", icon="✅")
                    # 把当前代码自动填入下方答疑的代码上下文，方便联动
                    st.session_state["code_context"] = code_content
                else:
                    error_detail = response.json().get("detail", "接口调用失败")
                    with analyze_result_box:
                        st.error(f"分析失败：{error_detail}")
            except requests.exceptions.ConnectionError:
                with analyze_result_box:
                    st.error("无法连接后端服务！请先启动FastAPI后端服务")
            except Exception as e:
                with analyze_result_box:
                    st.error(f"请求失败：{str(e)}")

# ========== 第二部分：RAG智能答疑功能 ==========
st.divider()
st.header("💬 编程智能答疑")
st.caption("基于知识库精准解答编程问题，支持关联上面的代码上下文")

# 初始化会话状态，保存历史对话，页面刷新不会丢失
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "code_context" not in st.session_state:
    st.session_state["code_context"] = ""

# 代码上下文展示与编辑
with st.expander("📎 代码上下文（可选，会和问题一起传给AI）", expanded=False):
    st.session_state["code_context"] = st.text_area(
        "相关代码上下文",
        value=st.session_state["code_context"],
        height=150,
        key="qa_code_context"
    )

# 展示历史对话
for chat in st.session_state["chat_history"]:
    with st.chat_message("user"):
        st.markdown(chat["question"])
    with st.chat_message("assistant"):
        st.markdown(chat["answer"])
        # 可折叠的引用内容
        with st.expander("查看引用的知识库内容", expanded=False):
            st.markdown(chat["reference"])

# 用户提问输入框
user_question = st.chat_input("请输入你的编程问题，例如：Python如何处理异常？")

# 提问逻辑
if user_question:
    # 先展示用户的问题
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # 调用后端接口生成答案
    with st.chat_message("assistant"):
        with st.spinner("正在检索知识库并生成答案..."):
            try:
                # 调用后端问答接口
                response = requests.post(
                    url=f"{BACKEND_BASE_URL}/api/rag-qa",
                    json={
                        "question": user_question,
                        "code_context": st.session_state["code_context"]
                    },
                    timeout=60
                )
                # 处理返回结果
                if response.status_code == 200:
                    result = response.json()["data"]
                    answer = result["answer"]
                    reference = result["reference"]
                    # 展示答案
                    st.markdown(answer)
                    # 展示引用内容
                    with st.expander("查看引用的知识库内容", expanded=False):
                        st.markdown(reference)
                    # 保存到历史对话
                    st.session_state["chat_history"].append({
                        "question": user_question,
                        "answer": answer,
                        "reference": reference
                    })
                else:
                    error_detail = response.json().get("detail", "接口调用失败")
                    st.error(f"提问失败：{error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("无法连接后端服务！请先启动FastAPI后端服务")
            except Exception as e:
                st.error(f"请求失败：{str(e)}")

# 清空对话按钮
if st.button("清空对话历史", type="secondary"):
    st.session_state["chat_history"] = []
    st.toast("对话历史已清空", icon="✅")
    st.rerun()
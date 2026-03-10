import streamlit as st
import requests

# 页面基础配置（必须放在最顶部）
st.set_page_config(
    page_title="代码学习智能审查助手",
    page_icon="💻",
    layout="wide"
)

# 后端接口地址（本地开发固定值，部署时再修改）
BACKEND_BASE_URL = "http://127.0.0.1:8000"

# 页面标题与说明
st.title("💻 代码学习智能审查助手")
st.caption("基于RAG与大模型的编程答疑系统 | 代码分析 · 问题解答")

# 分栏布局：左输入，右结果
col_input, col_result = st.columns([1, 1])

# 左侧：代码输入与功能区
with col_input:
    st.subheader("📝 代码输入区")
    # 编程语言选择
    lang = st.selectbox(
        "选择编程语言",
        options=["Python", "Java", "C++", "JavaScript"],
        index=0
    )
    # 代码输入框（全版本兼容，替代code_editor）
    code = st.text_area(
        label="请粘贴需分析的代码",
        height=350,
        placeholder=f"请输入{lang}代码，例如：\ndef add(a, b):\n    return a + b\n",
        key="code_input"
    )
    # 分析按钮
    analyze_btn = st.button(
        label="🔍 一键分析代码",
        type="primary",
        use_container_width=True
    )

# 右侧：结果展示区
with col_result:
    st.subheader("📊 分析结果展示")
    # 结果容器（带边框，提升观感）
    result_box = st.container(height=400, border=True)
    # 初始提示
    with result_box:
        st.info("请输入代码并点击「一键分析代码」查看结果")

# 核心逻辑：按钮点击后调用后端接口
if analyze_btn:
    # 入参校验
    if not code.strip():
        st.toast("⚠️ 请先输入有效代码！", icon="⚠️")
    else:
        with st.spinner("🤖 正在分析代码，请稍候..."):
            try:
                # 调用后端代码分析接口
                res = requests.post(
                    url=f"{BACKEND_BASE_URL}/api/code-analysis",
                    json={"code": code, "language": lang},
                    timeout=60
                )
                # 处理响应
                if res.status_code == 200:
                    analysis = res.json()["data"]
                    # 清空容器并展示结果
                    with result_box:
                        st.markdown(analysis)
                    st.toast("✅ 代码分析完成！", icon="✅")
                else:
                    # 后端错误处理
                    err_msg = res.json().get("detail", "后端接口调用失败")
                    with result_box:
                        st.error(f"分析失败：{err_msg}")
            except requests.exceptions.ConnectionError:
                # 后端未启动的专属提示（高频问题）
                with result_box:
                    st.error("❌ 无法连接后端服务！\n请先启动FastAPI后端（运行backend/main.py）")
            except Exception as e:
                # 其他异常
                with result_box:
                    st.error(f"❌ 分析出错：{str(e)}")

# 预留答疑区（Day3开发）
st.divider()
st.subheader("💬 编程智能答疑（开发中）")
st.write("Day3将实现基于RAG的编程问题精准解答功能，敬请期待！")
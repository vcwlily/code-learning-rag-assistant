from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import os

def split_markdown_documents(file_dir: str = "../data/raw_docs"):
    """
    处理markdown格式的编程文档，采用双层分块策略：
    1. 先按markdown标题拆分，保证语义完整性
    2. 再按固定字符数拆分，适配Embedding模型的输入长度
    """
    # 定义要拆分的标题层级，适配编程文档的结构
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    # 初始化分块器
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    # 二次分块，控制单块的长度，避免块太大丢失精度
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", " ", ""]
    )

    # 遍历文件夹里的所有markdown文件
    all_docs = []
    for filename in os.listdir(file_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(file_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                # 第一层：按标题拆分
                title_splits = markdown_splitter.split_text(markdown_content)
                # 第二层：按字符数拆分
                final_splits = text_splitter.split_documents(title_splits)
                all_docs.extend(final_splits)
            except Exception as e:
                print(f"处理文件{filename}失败：{str(e)}")
    return all_docs

# 本地测试用
if __name__ == "__main__":
    docs = split_markdown_documents()
    print(f"文档分块完成，共生成{len(docs)}个文本块")
    if docs:
        print(f"第一个块的内容预览：\n{docs[0].page_content[:100]}")
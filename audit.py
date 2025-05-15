import streamlit as st
import requests
import json
import pandas as pd
import PyPDF2
import io
import os
import datetime
from io import StringIO
import re
import time

# 设置页面配置
st.set_page_config(
    page_title="AI合规审核工具",
    page_icon="⚖️",
    layout="wide"
)

# 页面标题
st.title("⚖️ AI合规审核工具")
st.markdown("---")

# 初始化会话状态
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = {
        "法律法规": [],
        "区域政策": [],
        "行业标准": []
    }
    
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = []

# 侧边栏配置
st.sidebar.header("⚙️ 系统设置")

# API密钥输入
api_key = st.sidebar.text_input("DeepSeek API密钥", type="password")

# 模型选择
model = st.sidebar.selectbox(
    "选择模型",
    ["deepseek-chat", "deepseek-coder"]
)

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["📊 合规审核", "📚 知识库管理", "📜 审核历史"])

# 合规审核选项卡
with tab1:
    st.header("合规审核")
    
    # 审核类型选择
    audit_type = st.selectbox(
        "选择审核类型",
        ["劳动合规", "税务合规", "数据隐私", "环境合规", "知识产权", "自定义审核"]
    )
    
    # 区域选择
    region = st.selectbox(
        "选择区域",
        ["全国通用", "长三角地区", "珠三角地区", "京津冀地区", "西部地区", "东北地区"]
    )
    
    # 行业选择
    industry = st.selectbox(
        "选择行业",
        ["互联网", "制造业", "金融业", "教育", "医疗健康", "零售", "其他"]
    )
    
    # 文件上传区域
    st.subheader("上传审核文件")
    uploaded_files = st.file_uploader("上传PDF、Excel或文本文件", type=["pdf", "xlsx", "txt", "docx"], accept_multiple_files=True)
    
    # 文本输入区域
    st.subheader("或直接输入文本")
    input_text = st.text_area("输入需要审核的文本内容", height=150)
    
    # 高级选项
    with st.expander("高级选项"):
        thoroughness = st.slider("审核深度", 1, 5, 3)
        include_recommendations = st.checkbox("包含改进建议", value=True)
        include_legal_references = st.checkbox("包含法律条款引用", value=True)
        risk_scoring = st.checkbox("风险评分", value=True)
    
    # 审核按钮
    if st.button("开始合规审核"):
        if not api_key:
            st.error("请输入DeepSeek API密钥")
        elif not uploaded_files and not input_text:
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("正在进行合规审核，请稍候..."):
                try:
                    # 处理上传的文件
                    document_texts = []
                    
                    if uploaded_files:
                        for file in uploaded_files:
                            if file.name.endswith('.pdf'):
                                pdf_reader = PyPDF2.PdfReader(file)
                                text = ""
                                for page in pdf_reader.pages:
                                    text += page.extract_text()
                                document_texts.append(f"PDF文件 '{file.name}':\n{text}")
                                
                            elif file.name.endswith('.xlsx'):
                                df = pd.read_excel(file)
                                text = df.to_string()
                                document_texts.append(f"Excel文件 '{file.name}':\n{text}")
                                
                            elif file.name.endswith('.txt'):
                                text = file.read().decode('utf-8')
                                document_texts.append(f"文本文件 '{file.name}':\n{text}")
                    
                    if input_text:
                        document_texts.append(f"用户输入文本:\n{input_text}")
                    
                    # 获取相关知识库内容
                    relevant_laws = []
                    for law in st.session_state.knowledge_base["法律法规"]:
                        if audit_type.lower() in law["description"].lower() or audit_type.lower() in law["title"].lower():
                            relevant_laws.append(law)
                    
                    relevant_policies = []
                    for policy in st.session_state.knowledge_base["区域政策"]:
                        if region in policy["region"]:
                            relevant_policies.append(policy)
                    
                    # 构建提示词
                    knowledge_context = ""
                    if relevant_laws:
                        knowledge_context += "相关法律法规:\n"
                        for law in relevant_laws:
                            knowledge_context += f"- {law['title']}: {law['description']}\n"
                    
                    if relevant_policies:
                        knowledge_context += "\n相关区域政策:\n"
                        for policy in relevant_policies:
                            knowledge_context += f"- {policy['title']} ({policy['region']}): {policy['description']}\n"
                    
                    prompt = f"""
                    你是一位专业的AI合规审核专家，请对以下文档进行{audit_type}审核。

                    审核区域: {region}
                    行业: {industry}
                    审核深度: {thoroughness}/5
                    
                    {knowledge_context if knowledge_context else ""}
                    
                    需要审核的文档内容:
                    {"".join(document_texts)}
                    
                    请执行以下任务:
                    1. 识别所有潜在的合规风险点
                    2. 对每个风险点进行详细分析
                    3. 引用相关法律法规条款
                    4. 评估风险等级（高/中/低）
                    {"5. 提供具体的改进建议" if include_recommendations else ""}
                    {"6. 为每个风险点提供详细的法律依据" if include_legal_references else ""}
                    {"7. 为整体合规状况提供1-100的风险评分" if risk_scoring else ""}
                    
                    请以结构化的方式输出审核报告，包括摘要、详细分析和结论部分。
                    """
                    
                    # 调用DeepSeek API
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                    
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    }
                    
                    response = requests.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload)
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        audit_report = result["choices"][0]["message"]["content"]
                        
                        # 保存到审核历史
                        st.session_state.audit_history.append({
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "audit_type": audit_type,
                            "region": region,
                            "industry": industry,
                            "report": audit_report
                        })
                        
                        # 显示审核报告
                        st.subheader("📋 合规审核报告")
                        st.markdown("---")
                        st.markdown(audit_report)
                        
                        # 提供下载按钮
                        report_download = audit_report.encode()
                        st.download_button(
                            label="下载审核报告",
                            data=report_download,
                            file_name=f"合规审核报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                        
                    else:
                        st.error(f"API请求失败: {response.status_code}")
                        st.json(response.json())
                
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

# 知识库管理选项卡
with tab2:
    st.header("知识库管理")
    
    # 创建子选项卡
    kb_tab1, kb_tab2, kb_tab3 = st.tabs(["法律法规", "区域政策", "自动更新"])
    
    # 法律法规选项卡
    with kb_tab1:
        st.subheader("添加法律法规")
        law_title = st.text_input("法规名称", key="law_title")
        law_description = st.text_area("法规内容摘要", key="law_description")
        law_category = st.selectbox(
            "法规类别",
            ["劳动法", "税法", "公司法", "合同法", "知识产权法", "数据隐私法", "环境保护法", "其他"]
        )
        
        if st.button("添加法律法规"):
            if law_title and law_description:
                st.session_state.knowledge_base["法律法规"].append({
                    "title": law_title,
                    "description": law_description,
                    "category": law_category,
                    "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                st.success(f"已添加法律法规: {law_title}")
            else:
                st.error("请填写法规名称和内容")
        
        # 显示现有法律法规
        st.subheader("现有法律法规")
        if st.session_state.knowledge_base["法律法规"]:
            for i, law in enumerate(st.session_state.knowledge_base["法律法规"]):
                with st.expander(f"{law['title']} ({law['category']})"):
                    st.write(f"**类别:** {law['category']}")
                    st.write(f"**添加日期:** {law['added_date']}")
                    st.write(f"**内容摘要:** {law['description']}")
                    if st.button("删除", key=f"del_law_{i}"):
                        st.session_state.knowledge_base["法律法规"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("暂无法律法规，请添加")
    
    # 区域政策选项卡
    with kb_tab2:
        st.subheader("添加区域政策")
        policy_title = st.text_input("政策名称", key="policy_title")
        policy_region = st.selectbox(
            "适用区域",
            ["全国", "长三角地区", "珠三角地区", "京津冀地区", "西部地区", "东北地区", "其他"]
        )
        policy_description = st.text_area("政策内容摘要", key="policy_description")
        
        if st.button("添加区域政策"):
            if policy_title and policy_description:
                st.session_state.knowledge_base["区域政策"].append({
                    "title": policy_title,
                    "region": policy_region,
                    "description": policy_description,
                    "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                st.success(f"已添加区域政策: {policy_title}")
            else:
                st.error("请填写政策名称和内容")
        
        # 显示现有区域政策
        st.subheader("现有区域政策")
        if st.session_state.knowledge_base["区域政策"]:
            for i, policy in enumerate(st.session_state.knowledge_base["区域政策"]):
                with st.expander(f"{policy['title']} ({policy['region']})"):
                    st.write(f"**适用区域:** {policy['region']}")
                    st.write(f"**添加日期:** {policy['added_date']}")
                    st.write(f"**内容摘要:** {policy['description']}")
                    if st.button("删除", key=f"del_policy_{i}"):
                        st.session_state.knowledge_base["区域政策"].pop(i)
                        st.experimental_rerun()
        else:
            st.info("暂无区域政策，请添加")
    
    # 自动更新选项卡
    with kb_tab3:
        st.subheader("知识库自动更新")
        
        update_sources = st.multiselect(
            "选择更新来源",
            ["中国政府网", "国家法律法规数据库", "地方政府网站", "行业协会网站", "法律信息服务平台"]
        )
        
        update_frequency = st.selectbox(
            "更新频率",
            ["每日", "每周", "每月"]
        )
        
        if st.button("配置自动更新"):
            if update_sources and api_key:
                with st.spinner("正在配置自动更新..."):
                    time.sleep(2)  # 模拟处理时间
                    st.success("已成功配置知识库自动更新")
            else:
                st.error("请选择更新来源并确保已输入API密钥")
        
        # 手动更新按钮
        if st.button("立即更新知识库"):
            if api_key:
                with st.spinner("正在从选定来源获取最新法规和政策..."):
                    # 这里是模拟更新过程
                    time.sleep(3)
                    
                    # 模拟添加新的法律法规
                    new_laws = [
                        {
                            "title": "《中小企业促进法》2023年修订版",
                            "description": "新修订的《中小企业促进法》加强了对中小企业的财政支持和税收优惠政策，简化了行政审批程序。",
                            "category": "公司法",
                            "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        },
                        {
                            "title": "《数据安全法》实施细则",
                            "description": "明确了企业数据分类分级管理要求，规定了重要数据处理的安全评估程序。",
                            "category": "数据隐私法",
                            "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                    ]
                    
                    for law in new_laws:
                        if law not in st.session_state.knowledge_base["法律法规"]:
                            st.session_state.knowledge_base["法律法规"].append(law)
                    
                    # 模拟添加新的区域政策
                    new_policies = [
                        {
                            "title": "长三角地区企业社保缴纳统一标准",
                            "region": "长三角地区",
                            "description": "统一了上海、江苏、浙江、安徽地区企业社保缴纳基数和比例，简化了跨省市员工社保转移手续。",
                            "added_date": datetime.datetime.now().strftime("%Y-%m-%d")
                        }
                    ]
                    
                    for policy in new_policies:
                        if policy not in st.session_state.knowledge_base["区域政策"]:
                            st.session_state.knowledge_base["区域政策"].append(policy)
                    
                    st.success(f"知识库更新完成！新增法规 {len(new_laws)} 条，新增政策 {len(new_policies)} 条")
            else:
                st.error("请确保已输入API密钥")

# 审核历史选项卡
with tab3:
    st.header("审核历史记录")
    
    if st.session_state.audit_history:
        for i, audit in enumerate(reversed(st.session_state.audit_history)):
            with st.expander(f"{audit['timestamp']} - {audit['audit_type']} ({audit['region']}, {audit['industry']})"):
                st.markdown(audit['report'])
                
                # 提供下载按钮
                report_download = audit['report'].encode()
                st.download_button(
                    label="下载此报告",
                    data=report_download,
                    file_name=f"合规审核报告_{audit['timestamp'].replace(' ', '_').replace(':', '')}.md",
                    mime="text/markdown"
                )
    else:
        st.info("暂无审核历史记录")

# 页脚
st.markdown("---")
st.markdown("⚖️ AI合规审核工具 | 基于DeepSeek大模型和动态RAG知识库")
st.markdown("⚠️ 注意：本工具提供的审核结果仅供参考，不构成法律建议。重要决策请咨询专业法律顾问。")

# MultiModal_Rag

MultiModal_Rag/ <br>
├── example/ # azure_openai_api示例 <br>
│ <br>
├── HiQA/ # Hierarchy QA<br>
│ ├── backup/ # <br>
│ ├── build_tool/ # 格式（*.doc/*.ppt/*.pdf/*.csl）转换md<br>
│ ├── service/ # 查询服务<br>
│ ├── utils/ # 系统组件 <br>
│ ├── app_streamlit.py # 前端ui <br>
│ └── README.md # HiQA项目说明文件<br>
│<br>
├── .env/ # Jupyter Notebooks 文件 <br>
│<br>
├── .gitignore # 忽略列表 <br>
├── requirements.txt # 依赖包列表 <br>
└── README.md # 项目说明文件<br>
|<br>
|── datasets/ # 知识库文件 <br>
│ ├─<kb_name>/embeddings/ # 知识库嵌入 <br>
│ ├─<kb_name>/images/ # 知识库需要的图像 <br>
│ ├─<kb_name>/sections/ # 知识库切割的Section <br>
│ ├─<kb_name>/src_docs/ # 知识库需要的原始文件 <br>
│
|── datasrc/ # 入库原始文件 <br>
│ ├─<kb_name>/mds/ # 预训练模型用的MD文件 <br>
│ ├─<kb_name>/raw_docs/ # 原始打算入库的文件 <br>
│ ├─<kb_name>/raw_questions/ # 原始询问的问题 <br>


original HiQA: https://github.com/TebooNok/HiQA
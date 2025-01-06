## 配置 PYTEST 让 Test Explorer 能够看到
.vscode/settings.json 里面需要这样的配置
{
    "python.testing.pytestArgs": [
        "ctn2md_tests",
        "mrag_vdb_tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}

# FLOW Universal Orchestration Designer

一个**纯前端、单文件、可离线运行**的可视化编排设计器：双击 `index.html` 即可在浏览器中使用，无需任何后端服务。

设计器本身不内置任何编排方言——节点类型、表单字段、DAG 级配置、校验规则、代码生成模板、反解析器、提交逻辑**全部来自一份可上传的方言套件 Spec（YAML）**。当前默认内置并自动加载 **Airflow 3.x** 套件，打开即画。

[English](README.md)

## 特性

- **零依赖离线运行**：单个 HTML 文件，全部资源内联，`file://` 协议直接打开，解析与渲染都在浏览器内完成，零后端调用
- **Spec 驱动一切**：上传一份 YAML 套件即可切换方言（Airflow / DolphinScheduler / NiFi / LangGraph / 自有链路……），左侧调色板、右侧配置表单、Preview 代码随之整体切换
- **画布编排**：拖拽节点、连线建依赖、TaskGroup 分组、多种自动布局（Layered / Force / Tree / Radial）、小地图导航
- **实时代码生成**：Preview 面板实时渲染最终任务文件（如 Airflow DAG 的 Python），支持解锁手改，手改后为最终态
- **双向互转**：Upload Job 把已有任务文件（如 `.py` DAG）反解析回画布继续编辑；Export 把画布导出为任务文件下载
- **本地校验**：套件自带的校验规则在浏览器内实时运行，错误/警告即时提示
- **一键提交**：按套件 `submitJs` 契约把产物直发你配置的目标服务（浏览器直发，身份透传）

## 系统截图

### 主界面（Split 视图：画布 + 实时代码）

打开默认即 Split 模式：上半部分编排画布，下半部分实时渲染生成的 DAG 代码，中间分隔条可拖动。

![Split 视图](docs/images/01-split-overview.png)

### 画布视图与自动布局

`start → extract_orders → choose_path → recon_full/recon_fast → notify_team → end`，由 `docs/examples/order_recon.py` 反解析生成。

![画布视图](docs/images/02-canvas-dag.png)

### 节点配置表单（由 Spec 自动生成）

点选任意节点，右侧表单字段完全由该节点类型在 YAML 中的 `form` schema 驱动——新增节点类型只需写 YAML，零手写表单代码。

![节点配置](docs/images/03-node-config.png)

### Preview 代码视图

按套件方言模板实时渲染最终产物，本地校验通过后可直接下载或提交。

![Preview 视图](docs/images/04-preview-code.png)

## 如何使用

### 1. 打开页面

双击 `index.html`（或部署到任意静态托管，如 GitHub Pages）。打开后自动加载内置的 **Airflow 3.x 套件**，顶栏显示 `spec: airflow3-suite.yaml`。

### 2. 编排一个 DAG

1. 从左侧 **Vertices** 调色板把节点类型拖上画布（Airflow 套件内置 35 种）
2. 拖动节点边缘的连接点连线，建立任务依赖
3. 点选节点 / 连线 / 空白处，在右侧 **Config** 面板配置参数（节点表单、边条件、DAG 级字段）
4. Shift+拖选 ≥2 个节点后，可用左下角 **Group** 打成 TaskGroup
5. 顶部 **Canvas / Preview / Split** 切换视图；Preview 实时显示生成的 Python DAG
6. **Export** 下载产物，或 **Submit** 提交到套件配置的目标服务

### 3. 反解析已有 DAG

点 **Upload Job** 上传一个已有的 Airflow DAG `.py` 文件（可以试试 `docs/examples/order_recon.py`），画布里即刻还原出节点与依赖，可继续拖拽编辑后再导出。

### 4. 切换 / 试用心方言

点 **Upload Spec (YAML)**，从 `suites/` 目录任选一份套件上传即可整体切换方言：

| 文件 | 方言 |
| --- | --- |
| `suites/airflow3-suite.yaml` | Airflow 3.x（Python DAG） |
| `suites/ds-suite.yaml` | DolphinScheduler 3.x（JSON DAG） |
| `suites/langgraph-suite.yaml` | LangGraph（Python） |
| `suites/nifi-suite.yaml` | NiFi 2.x（flow.json） |
| `suites/askchain-suite.yaml` | Ask Chain（合成区间样例包） |
| `suites/dq-agentflow-suite.yaml` | DQ 问数链路（自有） |
| `suites/dq-taskflow-suite.yaml` | DQ 任务工作流（自有） |

## 仓库结构

```
.
├── index.html                  # 设计器本体（已内置 Airflow 3.x 套件，打开即用）
├── suites/                     # 方言套件 Spec（按需 Upload Spec 切换）
│   ├── airflow3-suite.yaml
│   └── ...
└── docs/
    ├── images/                 # README 截图
    └── examples/
        └── order_recon.py      # 示例 DAG，用于体验 Upload Job 反解析
```

> 想换默认加载的套件：把目标 YAML 全文替换 `index.html` 顶部 `<script>` 中 `window.__FLOW_AUTOSUITE__` 的 `suiteText` 字段即可。

## Spec 里包含了什么

一份套件 YAML 是**多文档 YAML**（`---` 分隔），遵循 `dq.platform/flow-meta/v1` 契约，包含三类文档：

### 1. `FlowGrammar`（语法规则，1 份）

定义这张画布的元规则：

- **`cycle`**：是否允许成环（Airflow 禁止，DSL 类引擎可放行回边 / 循环上限）
- **`degree`**：节点入度 / 出度上限
- **`group`**：分组机制（Airflow 的 TaskGroup），含分组字段 schema 与失败通知约定
- **`edge`**：边字段 schema（如 `condition` → 渲染为 `airflow.sdk.Label`）
- **`commonForm`**：所有节点共享的任务级字段（Airflow 套件 26 个：`owner`、`retries`、`trigger_rule`、`pool`、回调族等）
- **`dagFields`**：DAG 级字段（Airflow 套件 20 个：`start_date`、`schedule`、`catchup`、`max_active_runs`、`deadline` 等）

### 2. `FlowNodeType`（节点类型，N 份）

每份文档注册一种节点。Airflow 3.x 套件共 **35 种**，按目录分组：

| 分类 | 数量 | 代表 |
| --- | --- | --- |
| Scripts | 3 | PythonOperator、TaskFlowTask、BashOperator |
| Branching | 7 | BranchPythonOperator、ShortCircuitOperator、BranchSQLOperator… |
| Environments | 2 | PythonVirtualenvOperator、ExternalPythonOperator |
| Control | 4 | EmptyOperator、LatestOnlyOperator、ApprovalOperator… |
| Integration | 3 | EmailOperator、TriggerDagRunOperator、HttpOperator |
| Sensors | 9 | FileSensor、ExternalTaskSensor、HttpSensor… |
| Data / Data Quality | 1 + 5 | SQLExecuteQueryOperator、SQLTableCheckOperator… |
| Wildcard | 1 | ProviderWildcard（未注册算子的兜底） |

每个节点类型携带：`opClass`（算子类全路径）、`category` / `color`（调色板分组与配色）、`description`（含官方文档链接）、`form`（参数字段 schema）。

### 3. `FlowDialectTemplate`（方言模板，1 份）

定义"画布 ↔ 代码"的双向转换契约：

- **`skeleton` / `nodeRender` / `importRender` / `paramRender` / `edgeRender`**：代码生成模板（Handlebars 风格），决定 Preview 与 Export 的每一个字符
- **`validation`**：本地校验规则（Airflow 套件 6 条，如 `bash-command-nonempty`、`trigger-rule-branch-upstream`），在浏览器内实时执行
- **`parserJs`**：反解析器（JS 函数），把已有任务文件读回画布——Upload Job 的能力来源
- **`submitJs`**：提交契约，定义目标服务地址、凭证与发送方式
- **`target` / `targetVersions`**：目标引擎与版本范围（Airflow 套件：`airflow` 3.0 / 3.1 / 3.2）

## 如何自定义 Spec

### 最快速度：改一份现成的

复制 `suites/airflow3-suite.yaml` 另存为新文件，改完后在页面里 **Upload Spec (YAML)** 上传即可生效。解析、注册、渲染全部在浏览器内完成，改错会有明确报错，不会弄坏页面。

### 新增一种节点类型

在 YAML 末尾追加一个 `FlowNodeType` 文档：

```yaml
---
apiVersion: dq.platform/flow-meta/v1
kind: FlowNodeType
metadata: { name: SparkSubmitOperator, version: 1 }
spec:
  invocation: atomic
  managed: true
  color: orange
  category: Airflow/Integration
  description: Submit a Spark job. Docs - https://airflow.apache.org/docs/...
  opClass: airflow.providers.apache.spark.operators.spark_submit.SparkSubmitOperator
  form:
    application: { type: string, title: Application, required: true, description: Path to the Spark job }
    conf: { type: string, title: Spark Conf, format: expr, description: Dict expression of Spark configs }
    conn_id: { type: string, title: Connection ID }
```

保存 → 上传 → 调色板立刻出现该节点，右侧表单、代码生成自动生效。

### 字段 schema 词汇表

| type | 控件 | 说明 |
| --- | --- | --- |
| `string` | 单行输入 | 普通文本 |
| `number` | 数字输入 | 数值 |
| `boolean` | 开关 | 布尔 |
| `enum` | 下拉框 | 需配 `options: [...]` |
| `code` | 多行代码框 | 大段源码 / Markdown |
| `reference` | 引用 | 引用其他实体 |

`format` 修饰符：`expr`（Python 表达式原样透传）、`pylist`（逗号分隔 → Python 列表）、`pyref`（可调用引用）。辅以 `title`、`description`、`required`、`default` 控制表单展示与校验。

### 调整生成逻辑

- 改产物骨架 → 编辑 `FlowDialectTemplate` 的 `skeleton`
- 改某类节点的渲染分支 → 编辑 `nodeRender`（可按 `node.opClass` / 参数标记分支）
- 改导入行、参数行、边行 → `importRender` / `paramRender` / `edgeRender`
- 加"提交前自检" → 往 `validation` 里加规则（页面上实时跑）

### 调试建议

1. Preview 面板是最快的反馈环：改完套件上传，画布上的变化立刻反映在生成代码里
2. 本地校验面板会逐条列出 error / warning，先看它再导出
3. 语义正确性由套件作者负责——引擎只保证"按契约渲染"，建议生成的 DAG 先在真实 Airflow 环境里跑通一次再固化套件

## 未来期望

- **更多官方套件**：补齐 DolphinScheduler / NiFi / LangGraph 的反解析器与提交契约，覆盖 Airflow 更多 provider（Kubernetes、Docker、云厂商算子）
- **套件版本化与分发**：套件 registry + 版本管理，团队内共享、评审、灰度一套方言定义
- **与真实引擎直连**：从"提交文本"走向"直连 Airflow API"——远程 dry-validate、触发 DagRun、回读运行状态到画布
- **画布资产化**：画布快照持久化与分享（当前刷新即失）、模板库、常用子图复用
- **协作与评审**：多人协同编辑、变更 diff、套件与 DAG 的 PR 评审流
- **AI 辅助编排**：自然语言生成初始 DAG、参数自动补全、校验失败的智能修复建议
- **CI 集成**：套件 YAML 的契约测试进 CI，生成的 DAG 在流水线里做静态检查与 dry-run

## 注意事项

- 画布与 Preview 数据只存在于浏览器内存，**刷新即失**——重要产物请及时 Export
- Preview 解锁手改后为最终态，Export / Submit 均以 Preview 文本为准
- 渲染语义由套件作者负责，引擎只做契约内转换（页面上也有同样提示）

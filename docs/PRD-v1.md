# Memowell V1 — Product Requirements Document

**产品定位**: Text-first Copilot for Dementia Behavioral Events (语音辅助)
**目标用户**: 一线护工（CNA/nursing aide）、护士、护理机构管理者
**产品形态**: 三端统一 — Expo + Solito + Next.js monorepo，共享FastAPI后端。PWA (Next.js+Serwist) + Android + iOS 一套代码
**版本**: V1 MVP
**最后更新**: 2026-03-01

---

## 1. 问题定义

### 1.1 核心痛点

AD患者出现行为事件（拒药、agitation、日落综合征、wandering等）时：

1. **护工不知道怎么处理** — 培训不足，依赖口口相传的经验，不熟悉CMS/APA/NICE等权威指南
2. **交接班信息丢失** — 纸质交接本记录潦草、缺失，下一班不知道上一班发生了什么
3. **合规风险** — CMS检查发现文档不合规 → 罚款（单次可达$10K+）、星级降级
4. **干预缺乏闭环** — 做了什么干预、效果如何，没有结构化记录，无法优化

### 1.2 价值主张

> 减少交接失误 = 减少incident = 减少CMS罚款

- 护工语音口述 → 系统秒级返回合规处理步骤（RAG检索，不生成，零幻觉）
- 自动生成结构化事件日志 + 交接记录
- 下一班护工打开就能看到完整的 事件→干预→结果→后续建议

---

## 2. 用户角色

| 角色 | 描述 | 核心需求 |
|------|------|----------|
| **CNA/Aide** (一线护工) | 直接照护患者，英语可能非母语，手常常被占用 | 语音输入、简单指令、快速获取处理步骤 |
| **Charge Nurse** (当班护士) | 监督多个护工，负责药物管理和上报 | 查看班次总览、审核事件日志、签字确认 |
| **DON** (护理主任) | 负责合规、质量管理、CMS检查 | 合规报告、趋势分析、异常预警 |
| **Admin** (机构管理员) | IT/运营 | 用户管理、机构配置、数据导出 |

---

## 3. 核心用户流程 (V1 MVP)

### 3.1 行为事件处理流程（主流程）

```
[触发] 患者出现行为事件（如sundowning）
    ↓
[Step 1 - 语音报告] 护工按住麦克风按钮口述：
    "Mrs. Thompson 开始agitation了，在走廊来回走，
     拒绝回房间，情绪激动"
    ↓
[Step 2 - 语音转文字] Whisper STT → 结构化解析：
    - 患者: Margaret Thompson
    - 事件类型: Agitation + Wandering
    - 位置: 走廊
    - 时间: 自动记录
    ↓
[Step 3 - Protocol检索] RAG检索CMS/APA/NICE指南：
    - 匹配: "Agitation management in dementia patients"
    - 返回: 分步处理步骤（带来源引用）
    ↓
[Step 4 - 显示处理步骤] 护工看到：
    ┌─────────────────────────────────────┐
    │ 📋 Recommended Steps               │
    │                                     │
    │ 1. Approach calmly, use soft voice  │
    │ 2. Identify possible trigger        │
    │    (pain? hunger? environment?)     │
    │ 3. Redirect to familiar activity    │
    │ 4. If persists >15min, notify nurse │
    │ 5. Document intervention & outcome  │
    │                                     │
    │ 📎 Source: CMS F-Tag 604, APA §4.2 │
    └─────────────────────────────────────┘
    ↓
[Step 5 - 执行干预] 护工按步骤处理
    ↓
[Step 6 - 记录结果] 护工语音反馈：
    "用音乐转移注意力，10分钟后平静下来，
     回到房间休息了"
    ↓
[Step 7 - 自动生成] 系统生成：
    - 结构化事件日志 (Event → Intervention → Outcome)
    - 自动更新交接板
```

### 3.2 交接班流程

```
[班次结束]
    ↓
[自动汇总] 系统聚合本班次所有事件：
    ┌─────────────────────────────────────┐
    │ 🔄 Shift Handoff — Day → Evening   │
    │ 2026-02-28 15:00                    │
    │                                     │
    │ ⚠️ Margaret Thompson               │
    │   • Sundowning episode 14:20-14:35  │
    │   • Intervention: Music redirect ✅  │
    │   • Follow-up: Monitor mood at 16:00│
    │                                     │
    │ ✅ Robert Chen                       │
    │   • Stable day, no incidents        │
    │   • Medication taken on schedule    │
    │                                     │
    │ ⚠️ Dorothy Williams                 │
    │   • Refused afternoon medication    │
    │   • Rescheduled to evening — NOTIFY │
    └─────────────────────────────────────┘
    ↓
[接班护工] 打开App → 一屏看到所有重点
    ↓
[确认接收] 点击"Acknowledged"签收交接
```

---

## 4. 功能规格 (V1 MVP)

### 4.1 行为事件Copilot (核心功能)

**P0 — Must Have:**

| 功能 | 描述 |
|------|------|
| 语音输入 | 按住录音 → Whisper STT → 文字 |
| 事件解析 | 从自然语言中提取：患者、事件类型、严重度、位置 |
| Protocol RAG检索 | 检索CMS/APA/NICE/Alzheimer's Association指南，返回匹配的处理步骤+来源引用 |
| 结果记录 | 语音或文字记录干预措施和结果 |
| 事件日志 | Event → Intervention → Outcome 结构化存储 |

**P1 — Should Have:**

| 功能 | 描述 |
|------|------|
| 事件类型快捷按钮 | 常见事件一键选择（Agitation, Sundowning, Refusal, Fall, Wandering） |
| 严重度自动评估 | 基于描述自动判断 Low/Medium/High/Critical |
| 护士通知 | High/Critical事件自动推送给当班护士 |
| 多语言STT | 支持西语、中文等（护工多元化背景） |

### 4.2 智能交接板

**P0 — Must Have:**

| 功能 | 描述 |
|------|------|
| 班次交接摘要 | 自动汇总本班次所有事件，按患者分组 |
| 待办事项 | 上一班留下的follow-up items |
| 接收确认 | 接班护工签收 |
| 患者状态概览 | 每个患者当前状态一目了然（✅ 稳定 / ⚠️ 需关注 / 🚨 紧急） |

**P1 — Should Have:**

| 功能 | 描述 |
|------|------|
| 历史交接查看 | 回看过去7天交接记录 |
| 交接PDF导出 | 用于CMS检查存档 |

### 4.3 患者管理

**P0 — Must Have:**

| 功能 | 描述 |
|------|------|
| 患者列表 | 姓名、房间号、诊断、认知水平、照片 |
| 患者详情 | 行为事件历史、用药信息、特殊注意事项 |
| 事件时间线 | 按时间排列的事件日志 |

**P1 — Should Have:**

| 功能 | 描述 |
|------|------|
| 认知趋势图 | 基于事件数据的趋势变化 |
| 行为模式识别 | "Mrs. Thompson的sundowning通常在14:00-16:00发生" |

### 4.4 合规与报告 (V1.1)

暂不进入V1 MVP，但架构预留：

- CMS F-Tag合规检查
- Incident报告自动生成
- 星级评分影响预估

---

## 5. 技术架构

### 5.1 系统架构

```
┌──────────────────────────────────────────────┐
│        Frontend (Expo + Solito Monorepo)      │
│                                               │
│  packages/app/     共享screens + components   │
│  apps/expo/        Android + iOS (Expo)       │
│  apps/next/        Web/PWA (Next.js+Serwist)  │
│                                               │
│  iPad优先 / 手机兼容 / 三端一套代码            │
└────────────────────┬─────────────────────────┘
                     │ HTTPS REST API (共享)
┌────────────────────▼─────────────────────────┐
│               FastAPI Backend                 │
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ Event   │  │ Handoff  │  │  Protocol   │ │
│  │ Service │  │ Service  │  │ RAG Service │ │
│  └────┬────┘  └────┬─────┘  └──────┬──────┘ │
│       │            │               │         │
│  ┌────▼────────────▼───────────────▼──────┐  │
│  │           Data Layer                    │  │
│  │  SQLite (MVP) → PostgreSQL (scale)     │  │
│  │  ChromaDB / Qdrant (vector store)      │  │
│  └────────────────────────────────────────┘  │
│                                               │
│  External APIs:                               │
│  • Groq Whisper (STT)                        │
│  • Groq Llama 3.3 70B (事件解析/摘要)        │
│  • Edge-TTS (可选，语音播报步骤)              │
└───────────────────────────────────────────────┘
```

### 5.2 RAG Pipeline (Protocol检索)

```
[知识库构建 — 离线]
CMS Dementia Care Guidelines (PDF)
APA Clinical Practice Guideline (PDF)
NICE Dementia Guidelines (PDF)
Alzheimer's Association Care Standards (PDF)
State-specific regulations (PDF)
    ↓ 文档切片 + Embedding
    ↓ (chunk size ~500 tokens, overlap 50)
Vector Store (ChromaDB)

[实时检索 — 在线]
护工语音描述 → STT → 事件文本
    ↓ 提取关键词 + 事件类型
    ↓ Embedding → Vector similarity search
    ↓ Top-K chunks retrieved (K=5)
    ↓ Reranker (optional)
    ↓ 格式化输出：步骤 + 来源引用
    
⚠️ 关键原则：只检索，不生成。返回的步骤直接来自权威文档原文。
LLM仅用于：事件解析、格式化输出、摘要生成。
不用于：生成护理建议。
```

### 5.3 数据模型

```
Facility (机构)
├── id, name, address, license_number
├── shifts: [Day, Evening, Night] with times
└── settings: timezone, language, etc.

Patient (患者)
├── id, facility_id, name, room, photo
├── diagnosis, cognitive_level (MMSE/MoCA)
├── medications[], allergies[], special_notes
└── emergency_contact

CareStaff (护理人员)
├── id, facility_id, name, role (CNA/Nurse/DON)
├── current_shift, language_preference
└── credentials

BehavioralEvent (行为事件) — 核心数据
├── id, patient_id, reporter_id (CareStaff)
├── timestamp, shift_id
├── event_type: enum [Agitation, Sundowning, Refusal, 
│                      Wandering, Fall, Aggression, 
│                      Confusion, Sleep_Disturbance, Other]
├── severity: enum [Low, Medium, High, Critical]
├── description (原始语音转文字)
├── location
├── trigger (if identified)
├── protocol_matched: [{ source, section, steps[] }]
├── intervention: { description, timestamp }
├── outcome: { description, timestamp, resolved: bool }
└── follow_up: [{ note, assigned_to, due_time }]

ShiftHandoff (交接记录)
├── id, facility_id
├── from_shift, to_shift, handoff_time
├── events_summary[] (auto-generated)
├── pending_items[]
├── acknowledged_by, acknowledged_at
└── pdf_export_url

EventLog (Context → Intervention → Outcome)
├── event_id → BehavioralEvent
├── context: structured event data
├── intervention: what was done
├── outcome: result
└── ← 第二阶段核心数据资产
```

---

## 6. UI/UX 设计原则

### 6.1 核心理念：AI-Native，不是SaaS

> **结构化数据在后台，对话体验在前台。**
> 护工感觉在跟AI聊天，系统静默完成：事件分类、Protocol检索、C→I→O闭环、交接班数据。
> 绝不让护工产生"又要填表"的感觉，而是"这个挺好玩试试"的感觉。

**设计对标**: ChatGPT — 干净、白底、对话流、零学习成本

### 6.2 设计约束

- **手常被占用** → 语音+文字双向，单手操作
- **噪杂环境** → 大字体、高对比度、清晰视觉层级
- **英语可能非母语** → 简单词汇、图标辅助、未来多语言
- **紧急场景** → 最少点击到达关键信息（<3 taps）
- **护工已经被EHR/ERP折腾够了** → 不做表单，不做Dashboard，一切通过对话完成

### 6.3 页面结构：Chat-First（无底部Tab）

```
┌─────────────────────────────────────────┐
│ ☰ [Margaret Thompson ▾]    🔴2 ⚠️1     │  ← 顶部栏：左上角切换病人，右侧risk flags
├─────────────────────────────────────────┤
│                                         │
│  ┌─ 系统消息（灰色，小字）──────────┐   │
│  │ 📋 Today: 2 events, 1 pending   │   │
│  │ ⚠️ Last: Agitation at 14:20     │   │
│  └──────────────────────────────────┘   │
│                                         │
│  👤 "王阿姨7点拒吃药"                    │  ← 用户输入（语音/文字）
│                                         │
│  🤖 ┌─ 事件摘要条 ──────────────────┐   │
│     │ Medication Refusal · Med · 19:00│  │  ← 自动解析，灰色小摘要
│     └────────────────────────────────┘   │
│                                         │
│  🤖 ┌─ Protocol卡片 ────────────────┐   │
│     │ 📋 Recommended Steps          │   │
│     │ 1. Assess for pain/discomfort │   │
│     │ 2. Offer alternative timing   │   │
│     │ 3. Try with preferred food    │   │
│     │ 📎 CMS F-Tag 604, APA §4.2   │   │
│     └────────────────────────────────┘   │
│                                         │
│  🤖 ┌─ 快捷操作 ────────────────────┐   │
│     │ [✅ Confirm & Log]            │   │  ← 一键确认=写入事件日志+交接板
│     │ [🚨 Escalate]                 │   │  ← 通知DON/护士
│     │ [➕ Add Detail]               │   │  ← AI追问trigger/环境
│     └────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│ [🎤] [  Type a message...          ] ➤ │  ← 底部输入栏（文字+语音）
└─────────────────────────────────────────┘
```

### 6.4 交互流程

**核心循环：输入 → 3条推荐 → 一键确认**

```
护工说/打："王阿姨7点拒吃药"
    ↓
AI回复：
  ① 灰色摘要条 [Medication Refusal · Medium · 19:00]
  ② Protocol卡片（3条推荐步骤 + 来源引用）
  ③ 三个按钮：[✅ Confirm & Log] [🚨 Escalate] [➕ Add Detail]
    ↓
├─ 点 Confirm → 事件+干预自动写入日志和交接板，聊天流里出现"✅ Logged"
├─ 点 Escalate → 通知推送给DON/护士，聊天流里出现"🚨 Escalated to Nurse"
└─ 点 Add Detail → AI追问："What triggered this? Environment?"
    ↓ 护工补充 → 更新事件记录 → 再次3条推荐
```

**交接班 = 聊天流的自动摘要**
- 班次结束时，AI自动在聊天流中生成交接摘要卡片
- 或手动输入"generate handoff" → 生成本班次所有事件汇总
- 接班护工点 [✅ Acknowledge] 签收
- 不需要单独的Handoff页面

**病人切换（左上角 Drawer）**
- 点击左上角 → 侧边栏滑出
- 病人列表：按风险排序（🔴高风险在上）
- 显示：姓名 + 房间号 + 今日事件数 + 最后事件时间
- 切换病人 = 切换聊天上下文（像ChatGPT切换对话）
- 历史事件作为聊天消息流，往上滑动查看

### 6.5 消息类型

聊天流里混合五种消息：

| 类型 | 样式 | 触发 |
|------|------|------|
| **用户输入** | 右侧气泡（蓝色） | 护工语音/文字 |
| **事件摘要** | 灰色小条，居中 | 系统自动解析事件后 |
| **Protocol卡片** | 白色卡片+阴影 | 事件匹配到指南后 |
| **快捷操作按钮** | 横排按钮组 | 每次AI回复后 |
| **系统通知** | 灰色小字，居中 | ✅ Logged / 🚨 Escalated / 🔄 Handoff |

### 6.6 关键设计决策

| 决策 | 理由 |
|------|------|
| **无底部Tab** | Tab是SaaS思维，Chat-first不需要导航 |
| **无Dashboard** | 趋势/统计通过对话查询（"show me this week's summary"） |
| **无表单** | 所有输入通过自然语言，系统自动结构化 |
| **一键确认，不要求编辑** | 减少摩擦，护工不想修改AI解析的结果 |
| **3条推荐，不给长文** | 护工不看长文，3条足够，需要更多可追问 |
| **历史=聊天记录** | 往上滑就是历史，不需要单独的timeline页面 |

---

## 7. V1 MVP Scope & Timeline

### 7.1 MVP Scope (4-6周)

**Week 1-2: 基础架构**
- [ ] 数据模型 + SQLite/PostgreSQL
- [ ] 用户认证（简单PIN码 / 机构邀请码，不做复杂Auth）
- [ ] 患者CRUD
- [ ] RAG Pipeline搭建（ChromaDB + CMS/APA指南入库）

**Week 3-4: 核心功能**
- [ ] 行为事件报告（语音输入 → STT → 事件解析 → Protocol检索）
- [ ] 事件日志（Context → Intervention → Outcome）
- [ ] 交接板自动生成
- [ ] PWA前端（Events + Handoff + Patients三个Tab）

**Week 5-6: 打磨 + 三端上线 + Pilot准备**
- [ ] iPad适配优化
- [ ] 交接板PDF导出
- [ ] 基本错误处理 + 离线缓存（Serwist）
- [ ] Pilot部署包准备（给Wu老师的nursing home）

**三端上线 Milestone:**
- [ ] **Day 1**: PWA部署上线（Vercel，Next.js+Serwist）
- [ ] **Week 1**: Android → EAS Build → Google Play上线（$25开发者账号）
- [ ] **Week 2**: iOS → EAS Build → App Store上线（$99/yr，health category合规）

### 7.2 MVP不做的

- ❌ 复杂用户权限系统（V1用简单角色区分）
- ❌ EHR双向集成（V2，但V1提供CSV导入/导出）
- ❌ 多机构支持（V1单机构）
- ❌ 患者陪伴聊天（保留代码，不进V1主流程）
- ❌ 合规报告生成（V1.1）
- ❌ UI美化（Wu: 先做AI feature，UI后调）

### 7.3 成功指标

| 指标 | 目标 |
|------|------|
| 事件记录完成率 | >80%（护工愿意用它记录） |
| 平均记录时间 | <2分钟/事件（vs 纸质5-10分钟） |
| 交接信息遗漏率 | 减少50%（vs 纸质交接） |
| Protocol匹配准确率 | >90%（检索到正确指南段落） |
| 护工净推荐值(NPS) | >30 |

---

## 8. 三阶段路线图

### Phase 1 — 工具 (Now → 6个月)
- 行为事件Copilot + 自动交接记录
- 单机构Pilot验证
- 收入模式：Per-bed/month SaaS ($5-15/bed/month)

### Phase 2 — 数据 (6-18个月)
- 积累 Context → Intervention → Outcome 闭环数据
- 这种结构化行为干预数据是现有EHR几乎不具备的
- 关键挑战：设计让护工自然完成反馈闭环的UX
- 多机构扩展

### Phase 3 — 平台 (18-36个月)
- 干预策略排序（哪种干预对哪种事件最有效）
- 风险预测（基于行为模式预测即将发生的事件）
- 护理策略仿真与优化
- 数字孪生 + World Model

---

## 9. 融资叙事（与产品分开执行）

**Vision**: AD护理的数字孪生和World Model

每个患者都有认知数字孪生，可以：
- 预测病程轨迹
- 优化个性化护理方案
- Simulation培训护工
- 类似nursing home的operating system

Phase 1的Copilot = 数据入口
已完成的Patient Companion demo = 患者端原型
最终两侧数据汇合 → 完整的护理World Model

---

## 10. 数据导入/集成策略 (03/01 Wu反馈)

> Wu核心观点：如果换平台太麻烦，护理机构和医院都不会考虑新AI产品。入门成本高=没人用。竞争者可能比我们引入客户的方式更简单方便。

### 10.1 Onboarding Friction = 生死问题

养老机构病人流动性低（Wu/Kai确认），意味着：
- ✅ 一旦onboard，数据持续积累，switching cost高，retention天然好
- ❌ 但如果初始导入太痛苦，机构根本不会尝试

### 10.2 V1 MVP 数据导入方案

**P0 — Must Have (V1):**

| 功能 | 描述 |
|------|------|
| CSV/Excel批量导入 | 上传病人名单（姓名、房间号、诊断、认知水平），一键建档 |
| 手动新建患者 | 没有电子记录的患者可以直接在App里新建 |
| 护工批量导入 | CSV上传护工名单（姓名、角色、班次） |

**P1 — Should Have (V1.1):**

| 功能 | 描述 |
|------|------|
| 数据导出 | 事件日志、交接记录导出为CSV/PDF，方便给CMS检查或迁移 |
| 模板下载 | 提供标准Excel模板，机构填好直接上传 |

**P2 — V2 EHR集成:**

| 功能 | 描述 |
|------|------|
| HL7 FHIR API | 与主流养老院EHR系统对接（PointClickCare, MatrixCare, Yardi） |
| 双向同步 | 患者数据从EHR拉取，事件记录推回EHR |
| SSO/LDAP | 机构统一账号登录 |

### 10.3 Voice ↔ Text 双向 (Wu反馈)

V1已实现Text-first + 语音辅助。需增强：
- **Text → Voice**: Protocol推荐步骤可以语音播报（Edge-TTS），护工手忙时听着做
- **Voice → Text**: 已有Whisper STT
- 两个方向自由切换，适配不同场景（安静办公室用文字，忙碌现场用语音）

### 10.4 Automatic Summarization 作为核心卖点 (Wu/Kai共识)

LLM功能不是附加feature，是核心卖点。V1需要突出展示：
- ✅ 事件自动摘要（已有：LLM post-processing raw events → structured summary）
- ✅ 交接报告自动生成（已有：shift handoff auto-generation）
- 🔲 班次趋势摘要（"本周agitation事件比上周增加30%，主要集中在14:00-16:00"）
- 🔲 患者行为模式识别（"Mrs. Thompson的sundowning与午餐后服药时间相关"）

**Demo展示策略**: 打开App → 第一屏就看到AI生成的摘要和洞察，不是传统的手动输入表单

---

## 11. 外部资源与合作 (03/01更新)

### 11.1 Wu的学术网络
- Wu分享了Alzheimer's Association官方资源
- Wu有一位**护理学院同事**（Dementia非其专长，但可辅助护理流程验证）
- Wu计划实地考察nursing home对比内部protocol标准

### 11.2 Alzheimer's Association
- 官方指南可补充RAG知识库
- 潜在合作/背书渠道
- StartUp Health Alzheimer's Moonshot项目

---

## 12. 开放问题

1. **数据存储**: 护理数据需要HIPAA合规，V1阶段怎么处理？建议先用de-identification + 机构自托管
2. **离线支持**: Nursing home WiFi不一定稳定，语音录制需要离线缓存，联网后同步
3. **iPad vs 手机**: Pilot时用哪种设备？建议先iPad（护士站常备），手机作为辅助
4. **Protocol更新**: CMS指南会更新，RAG知识库需要版本管理
5. **多语言优先级**: 西班牙语应该是第一个加的（大量Hispanic护工）
6. **数据迁移摩擦** (03/01 Wu): 如何让初始onboarding足够简单？CSV模板+一键导入是底线，长期需EHR集成
7. **现有交接方式竞争** (03/01 Wu): WhatsApp+白板是现有baseline，我们需要比这更简单而不是更复杂
8. **Cross-platform UI** (03/01 Wu): 不同设备屏幕适配，当前表格空位太多需优化（但Wu也说先做AI feature，UI后调）

---

*Document version: 1.1*
*Authors: Guilin Zhang, 参谋 (AI Copilot)*
*Stakeholders: Dr. Dezhi Wu (USC), Kai Zhao*

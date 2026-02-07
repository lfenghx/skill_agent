## Skill Agent

**作者：** lfenghx  
**版本：** 0.0.3
**类型：** Tool（工具插件）

### 简介

Skill Agent 是一个基于 “Skill 渐进式披露（Progressive Disclosure）” 设计的通用型工具插件：它把本地 `skills/` 目录当作“工具箱”，让大模型在需要时逐步读取技能说明、再按需读取文件/执行脚本，最终生成文本或文件交付。

### 适用场景

- 你希望接入Skill，用“说明书（SKILL.md）+ 文件结构 + 脚本”来约束/增强大模型执行能力
- 你希望输出带有进度提示，并把生成的文件作为工具输出返回
- 你希望把技能封装成可复用的目录（Reference、Scripts 等），而不是把所有逻辑写死在提示词里

### 功能特性

- 渐进式披露：先用技能索引判断，再读取 SKILL.md，再按需读文件/执行命令
- 文件交付：Agent结束时会把本次 temp 会话目录中的文件作为文件输出返回
- 自由执行：Agent可以执行任意命令，包括但不限于读取文件、写入文件、执行脚本等
- 可控记忆：Agent可设定记忆长度，可执行轮次深度等

### 工具参数

本插件共有两个工具
“技能管理”：用于管理技能目录，可查看技能，新增技能，删除技能。
![alt text](_assets/image-0.png)
“agent_skill”：通用智能体，可用于执行已存入的技能。
![alt text](_assets/image-1.png)

### 使用方式（在 Dify 中）

第一步：在市场中直接安装此插件
第二步：自托管用户在dify的.env中将Files_url设置为你的dify地址，否则dify获取不到你上传的文件
第三步：编排工作流，如下图
![alt text](_assets/image-2.png)
第四步：管理技能
![alt text](_assets/image-3.png)
第五步：与Skill_Agent交互
![alt text](_assets/image-4.png)

视频讲解地址：https://www.bilibili.com/video/BV1iszkBCEes

### Skill 标准规范

- 每个 skill 必须包含 `SKILL.md`（支持 YAML Frontmatter：`name`、`description`）
- `SKILL.md` 里可以定义触发条件、流程、需要读取的参考文件、需要执行的脚本命令、交付物规范等

### 更新历史

- 0.0.3：支持Agent流式输出，支持Agent跨轮次交互式对话，支持node.js脚本运行，提升Agent运行稳定性
- 0.0.2：支持Agent文件上传，解析，支持依赖自行安装
- 0.0.1：实现技能管理，按渐进式披露方式工作的通用型Agent

### 作者与联系

- GitHub：lfenghx（仓库：<https://github.com/lfenghx/skill_agent>）
- B 站：元视界\_O凌枫o
- 邮箱：550916599@qq.com

# CISC 7403 Project II 运行说明（在课程虚拟机上执行）

本说明按顺序列出你需要在 Ubuntu 虚拟机上执行的命令，并标出**每一步对应哪张截图、截什么画面、放进报告哪一节**。
所有需要实机测量才能得到的数字，在报告里都用红色 `[待填]` 标出，命令见第 6 节。

> 约定：下文假设你把 `outputs/code/` 整个目录上传到了虚拟机，路径为 `~/cisc7403-p2/`（可自行改名，后续命令同步修改）。

---

## 0. 交付物清单

```
outputs/
├── code/                          # 提交给老师的完整源码
│   ├── backend/                   # 后端应用 + Dockerfile
│   ├── nginx/                     # nginx.conf（双后端）、nginx.single.conf（单后端基准）
│   ├── scripts/                   # verify_lb.sh / fault_tolerance.sh / bench.sh
│   ├── docker-compose.yml         # 三容器部署（lb + backend1 + backend2）
│   ├── docker-compose.single.yml  # 仅用于性能实验的单后端部署
│   └── README.md
├── report/                        # 英文 LaTeX 报告
│   ├── main.tex
│   └── figures/                   # 5 张占位图（其中 3 张需要你用截图替换）
├── role-declaration/
│   └── CISC7403_Role_Declaration.docx   # 已按本作业分工预填，只需改姓名/学号
└── RUNBOOK_zh.md                  # 本文件
```

---

## 1. 准备虚拟机环境

### 1.1 安装 Docker Engine 与 Compose 插件

```bash
sudo apt update
sudo apt install -y curl
curl -fsSL https://get.docker.com | sudo sh          # 官方一键脚本，安装 docker + compose 插件
sudo systemctl enable --now docker
sudo usermod -aG docker $USER                        # 让当前用户免 sudo 使用 docker
```

**执行完必须退出 SSH 重新登录一次**（`usermod` 才会生效），然后验证：

```bash
docker --version
docker compose version        # 必须能看到 "Docker Compose version v2.x"
```

> 如果 `docker compose version` 报错，说明安装的是旧版 `docker-compose`（v1，命令带横线），请用上面的官方脚本重装。

### 1.2 上传代码

在你自己的电脑上执行（把 `user@vm-ip` 换成虚拟机地址）：

```bash
scp -r outputs/code user@vm-ip:~/cisc7403-p2
```

或先压缩再传：

```bash
# 本机
zip -r code.zip code
scp code.zip user@vm-ip:~/
# 虚拟机
cd ~ && unzip -q code.zip -d cisc7403-p2-part && mv cisc7403-p2-part/code ~/cisc7403-p2
```

确认文件齐全：

```bash
cd ~/cisc7403-p2
find . -maxdepth 2 -type f | sort
```

应能看到 `docker-compose.yml`、`docker-compose.single.yml`、`backend/{app.py,Dockerfile,requirements.txt}`、`nginx/{nginx.conf,nginx.single.conf}`、`scripts/*.sh`。

### 1.3 安装压测工具 wrk（性能实验需要）

```bash
sudo apt install -y wrk
wrk -v || true
```

若源里没有 `wrk`，用源码编译（约 1 分钟）：

```bash
sudo apt install -y build-essential libssl-dev git
git clone https://github.com/wg/wrk.git ~/wrk-src
cd ~/wrk-src && make -j4 && sudo cp wrk /usr/local/bin/
```

### 1.4 给脚本执行权限

```bash
cd ~/cisc7403-p2
chmod +x scripts/*.sh
```

---

## 2. 启动三容器系统

```bash
cd ~/cisc7403-p2
docker compose up --build -d
docker compose ps
```

**预期**：`docker compose ps` 显示 3 个容器 `Up`，其中只有 `lb` 有端口映射 `0.0.0.0:6120->6120/tcp`，`backend1` / `backend2` 的 PORTS 列为 `8000/tcp`（只是声明，没有对外发布）。

自检（不截图，确认服务通）：

```bash
curl -s http://localhost:6120/ ; echo
```

应返回类似 `{"endpoint":"/","hostname":"...","instance":"backend1",...}` 的 JSON。

> **截图 0（可选，但推荐）**：`docker compose ps` 的完整输出，能看到 3 个容器和 `6120->6120/tcp`。
> 若报告里还有空位，可保存为 `report/figures/shot_deployment.png`，再按 `main.tex` 第 2.3 节里那段被注释掉的 `figure` 环境取消注释（否则不用管它，报告默认不含这张图）。

---

## 3. 负载均衡验证  →  报告第 3 节（图 2）

```bash
for i in $(seq 1 10); do curl -s http://localhost:6120/ ; echo ; done
```

或直接跑脚本（输出更整洁，并给出统计）：

```bash
./scripts/verify_lb.sh          # 默认发 10 个请求；N=20 ./scripts/verify_lb.sh 可改数量
```

**预期**：`"instance"` 字段在 `backend1` 与 `backend2` 之间交替出现，例如
`backend1, backend2, backend1, backend2, ...`。

**截图 1 —— 报告图 2**
| 项目 | 内容 |
|---|---|
| 执行的操作 | 上面的 `for ... curl ... done` 循环 |
| 截什么画面 | 终端里这 10 行返回结果（能看到 backend1 / backend2 交替出现即可，多截一点上下文更好） |
| 保存为 | `report/figures/shot_load_balancing.png`（**覆盖同名占位图**） |
| 放在报告 | 第 3 节 Load-Balancing Verification，图 2 |
| 顺带记录 | 10 个请求里 backend1 几个、backend2 几个 → 填报告里的 `[N]` `[n1]` `[n2]` |

可选补充证据（不占报告版面）：`docker compose logs --tail=20 backend1 backend2` 会看到每个请求的一行日志。

---

## 4. 故障容错实验  →  报告第 4 节（图 3）

### 4.1 先确认两个后端都在服务

```bash
docker compose ps
for i in 1 2 3; do curl -s http://localhost:6120/ ; echo ; done
```

### 4.2 停掉 backend2，服务应继续可用

```bash
docker stop backend2
docker compose ps                                   # backend2 应为 Exited
for i in $(seq 1 6); do curl -s http://localhost:6120/ ; echo ; done
```

**预期**：6 个请求**全部成功**，且 `"instance"` 全是 `backend1`（Nginx 把到坏节点的连接重试到健康节点）。

**截图 2 —— 报告图 3 左**
| 项目 | 内容 |
|---|---|
| 执行的操作 | `docker stop backend2` + `docker compose ps` + 6 次 curl |
| 截什么画面 | 同一屏内能看到 backend2 已停止（Exited）**以及** curl 仍然返回 `backend1` |
| 保存为 | `report/figures/shot_fault_stopped.png` |
| 放在报告 | 第 4 节 Fault-Tolerance Experiment，图 3 左 |
| 顺带记录 | 期间成功请求数 k → 填报告 `[k]` |

### 4.3 恢复 backend2

```bash
docker start backend2
sleep 3
docker compose ps
for i in 1 2 3 4; do curl -s http://localhost:6120/ ; echo ; done
```

**预期**：请求重新在 `backend1` 与 `backend2` 之间交替，**不需要重启 Nginx**。

**截图 3 —— 报告图 3 右**
| 项目 | 内容 |
|---|---|
| 执行的操作 | `docker start backend2` + `docker compose ps` + 4 次 curl |
| 截什么画面 | backend2 恢复 Up，且 curl 结果重新出现 `backend2` |
| 保存为 | `report/figures/shot_fault_restored.png` |
| 放在报告 | 第 4 节，图 3 右 |

> 报告第 4 节里有一句"故障期间平均延迟 `[ms]` 对比正常 `[ms]`"。如果你不想做这个测时，**直接把括号里那半句删掉**即可（不是必交内容）；若要测，可在停止 backend2 前后各跑一次 `./scripts/verify_lb.sh`，用 `time curl -s -o /dev/null http://localhost:6120/` 粗看单次耗时。

---

## 5. 性能实验  →  报告第 5 节（表 2）

两次实验必须用**完全相同的负载参数**：`wrk -t2 -c20 -d10s`。

### 5.1 配置 A：2 个后端

```bash
docker compose up -d --build
docker compose ps                         # 确认 3 个容器都在
wrk -t2 -c20 -d10s http://localhost:6120/work
```

**记录**输出里的两个数：
- `Requests/sec:` → 表 2 "Throughput (req/s)"
- `Latency ... Avg:` → 表 2 "Average Latency (ms)"

### 5.2 配置 B：1 个后端

```bash
docker compose down
docker compose -f docker-compose.single.yml up -d --build
docker compose -f docker-compose.single.yml ps     # 只有 lb + backend1
wrk -t2 -c20 -d10s http://localhost:6120/work
```

同样记录 `Requests/sec` 与 `Latency Avg` → 表 2 第 1 行。

> 注意：单后端配置用的是 `nginx.single.conf`（upstream 里只有一个 server）。如果在同一个 nginx.conf 里留一个死节点，Nginx 会把请求重试到活的那个，测出来的"单后端"就失真了。

### 5.3 恢复三容器部署

```bash
docker compose -f docker-compose.single.yml down
docker compose up -d
```

**一键版（推荐，省去手工切换）**：

```bash
./scripts/bench.sh          # 依次跑 2 后端 / 1 后端，原始输出存到 results/wrk_*.txt
```

无论手工还是脚本，跑完请把两份原始输出保留下来（报告默认只放表 2，原始 wrk 输出可作为补充证据）。

> **截图 4（可选）**：`wrk` 的完整输出（含 Requests/sec 与 Latency）。
> 报告为控制在 3 页内，**默认没有放这张图**。如果老师要求附原始输出、或你删掉了别的内容腾出空间，可保存为
> `report/figures/shot_wrk_2backends.png` / `shot_wrk_1backend.png`（这两个占位文件已在 `figures/` 中，直接在报告里加一个 figure 环境即可）。

---

## 6. 填写报告中的 `[待填]` 项

打开 `report/main.tex`，搜索红色标记 `\pending{`，逐项替换（改完记得把 `\pending{...}` 整个替换成数字/文字，不要留下红框）：

| 位置 | 待填内容 | 来自哪一步 |
|---|---|---|
| 封面 | 队伍编号、成员姓名+学号、日期 | 你们自己的信息 |
| 第 3 节正文 | `\pending{N}`、`\pending{n1}`、`\pending{n2}` | 第 3 节 10 个请求的统计 |
| 第 4 节正文 | `\pending{k}`（故障期间成功请求数）、两处 `\pending{ms}` | 第 4.2 节 |
| 表 2（表 \ref{tab:perf}） | 4 个数字：1 后端 / 2 后端的吞吐与平均延迟 | 第 5.1、5.2 节 |
| 第 5 节正文 | `\pending{x.x}`×2（吞吐倍数、延迟降低倍数） | 用表 2 的数字相除 |
| 第 6 节 Contributions | 成员姓名 + 贡献百分比 | 你们自己商定 |
| `role-declaration/*.docx` | 队伍编号、成员姓名、互评分数、反思段落 | 你们自己商定 |

**建议的写作口径**（避免编造）：
- 若实测吞吐约为单后端的 1.8–2.0 倍、平均延迟约为一半，直接按实测写，不需要凑整；
- 若实测偏差较大（例如虚拟机 CPU 只有 1–2 核），照实写，并在第 6 节"Discussion"里说明噪声来源（其他进程、CPU 核数、Nginx 也占 CPU）。

---

## 7. 替换报告里的图片

`report/figures/` 里 5 个 PNG，其中 3 个必须换成你的实机截图（**文件名保持不变**，LaTeX 无需改动）：

| 文件名 | 是否需要替换 | 对应报告位置 |
|---|---|---|
| `shot_load_balancing.png` | **必须** | 图 2（第 3 节） |
| `shot_fault_stopped.png` | **必须** | 图 3 左（第 4 节） |
| `shot_fault_restored.png` | **必须** | 图 3 右（第 4 节） |
| `shot_wrk_2backends.png` | 可选（报告默认未引用） | 第 5 节，如需自行加图 |
| `shot_wrk_1backend.png` | 可选（报告默认未引用） | 第 5 节，如需自行加图 |

图 1 是 TikZ 矢量图（架构图），不需要截图。

**截图建议**：
- 用终端截取，**裁掉无关的桌面/边框**，只保留命令行与输出；
- 深色主题也行，但三张图风格统一更好看；
- 如果换图后页数超过 3 页（不含封面），优先裁剪截图上下空白。

---

## 8. 编译报告

### 方式 A：本机 / 虚拟机装 TeX Live

```bash
sudo apt install -y texlive-latex-extra texlive-pictures texlive-lang-english latexmk
cd report
latexmk -pdf main.tex            # 生成 main.pdf
```

没有 `latexmk` 时手工编译两次（目录交叉引用需要两遍）：

```bash
pdflatex main.tex && pdflatex main.tex
```

### 方式 B：Overleaf

把整个 `report/` 目录（含 `figures/`）压缩上传，主文件设为 `main.tex`，编译器选 pdfLaTeX。

**编译结果自检**：应生成 **封面 1 页 + 正文 3 页**（作业要求正文 ≤ 3 页，不含封面）。若你的截图较高导致溢出到第 4 页，优先裁剪截图或删掉第 4 节里可选的那句延迟对比。

---

## 9. 提交清单

- [ ] `code/`（`app.py`、`Dockerfile`、`requirements.txt`、`nginx.conf`、`nginx.single.conf`、`docker-compose.yml`、`docker-compose.single.yml`、`scripts/`）
- [ ] `report/main.pdf`（+ `main.tex` 与 `figures/`）
- [ ] `CISC7403_Role_Declaration.docx`（已填姓名、互评、反思并签名）
- [ ] 原始 `wrk` 输出（`results/wrk_*.txt`，如老师要求）

---

## 附录 A：常见问题

| 现象 | 原因 / 处理 |
|---|---|
| `Bind for 0.0.0.0:6120 failed: port is already allocated` | 6120 被别的进程占用：`sudo ss -lptn 'sport = :6120'` 找到进程，或 `docker compose down` 清掉旧容器 |
| `docker compose ps` 只有 2 个容器 | `docker compose up --build -d` 没跑完，看 `docker compose logs lb` / `logs backend2` |
| 启动后立刻 `502 Bad Gateway` | backend 还在启动（Flask 启动约 1 秒）。`docker compose logs backend1` 应打印 `* Running on http://0.0.0.0:8000`；稍等再 curl |
| `permission denied while trying to connect to the Docker daemon socket` | 没有重新登录 SSH，或没用 `usermod -aG docker $USER`；临时可用 `sudo docker ...` |
| `docker compose` 提示 `unknown command` | 装的是 v1；按 1.1 用官方脚本重装 v2 插件 |
| `wrk: command not found` | 见 1.3，源码编译后 `sudo cp wrk /usr/local/bin/` |
| 停掉 backend2 后 curl 偶尔很慢（约 1 秒） | 正常现象：Nginx 先尝试连接已关闭的地址，`proxy_connect_timeout 1s` 超时后重试到健康节点 |
| 构建时 pip 很慢 | 用镜像源：`docker compose build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple` |
| 想改对外端口 | 同时改 `docker-compose.yml` 的 `ports` 和 `nginx/nginx.conf` 的 `listen`（以及 `docker-compose.single.yml`、`nginx.single.conf`） |

## 附录 B：这套代码为什么满足作业要求（对照表）

| 作业要求 | 实现位置 |
|---|---|
| 两个后端同一镜像、同一应用 | `docker-compose.yml` 中两个服务共用 `x-backend` 锚点（同 build context、同 image tag），仅 `INSTANCE_NAME` 不同 |
| `/` 返回实例标识 | `backend/app.py` 的 `index()`，返回 `instance` / `hostname` / `pid` |
| `/work` 约 50 ms | `time.sleep(WORK_DELAY_SECONDS)`，默认 `0.05` |
| 单进程、关闭多线程（`threaded=False`） | `app.run(..., threaded=False, processes=1, use_reloader=False)` |
| 后端不向宿主机发布端口 | 两个后端只有 `expose: "8000"`，无 `ports` |
| 后端日志可看 | 每个请求 `app.logger.info(...)`，`docker compose logs` 可见 |
| Nginx 独立容器 + upstream 两个后端 | `nginx/nginx.conf`：`upstream backend_pool { server backend1:8000; server backend2:8000; }` |
| 只用 compose 服务名互相访问 | upstream 用 `backend1` / `backend2`，由 Docker 内嵌 DNS 解析 |
| 只暴露 6120 | 仅 `lb` 有 `"6120:6120"` |
| 单命令启动 | `docker compose up --build` |
| 某后端宕机仍可用 | `proxy_next_upstream error timeout http_502 http_503 http_504` |

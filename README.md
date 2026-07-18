# Modifier-for-CaoCaoZhuan

## 6.6 适配说明

本目录仍是原作者的 Python/PyQt5 旧扳手工程。窗口保持 `700×530`、八个原页面、原对象名、原控件几何和准星拖拽方式，不迁移到其它编辑器，也不修改磁盘上的游戏 EXE 或资源文件。

自动模式现支持 `FilePrivatePart=6` 的 32 位 `Ekd5.exe`。识别流程为 PE32/x86 与模块检查、版本资源、已知 SHA 标注、逐功能唯一签名、原字节检查和附加后的运行时表探针。地址以参考 VA/RVA 保存，并按实际模块基址换算。按当前试用策略，所有 6.6（包括未知派生版）默认开放原 UI；签名和证据状态只用于状态说明，不再禁用控件。

完整能力与未闭环项目见 [CAPABILITY_MATRIX.md](CAPABILITY_MATRIX.md)，自动测试和实机待测项见 [ACCEPTANCE_66.md](ACCEPTANCE_66.md)，证据采集步骤见 [EVIDENCE_GUIDE.md](EVIDENCE_GUIDE.md)。

6.6 能力证据状态依次为 `Unavailable`、`StaticVerified`、`RuntimeVerified`、`Enabled`。状态仍表示定位和实机可信度，但不再作为运行门禁：状态栏显示 `强制试用 23 / 已定位 22 / 旧地址 1`，所有原控件仍保留。当前两个基底有 22 项静态通过、1 项尚无静态配方；没有最终实测配方的按钮会说明原因并拒绝错误写入。

### 6.6 天赋分配布局

6.6 天赋分配主表由 `DWORD[0x00500C3B]` 指向，当前两个基底均解析为 `0x00511000`。每个特效占 `0x10` 字节，包含四组 `角色 UInt16 + 特效值 UInt8` 和两组 `兵种 UInt8 + 特效值 UInt8`。角色 ID `0..1023` 有效；不同派生版运行时使用 `1024` 或 `1025` 表示空，扳手附加后扫描完整分配表识别当前空值，UI 统一显示为“空”，保存时按当前进程的原始编码写回。兵种 `0..79` 有效，读取到 `80` 及以上时显示为空，保存统一写 `255`。

天赋页在 6.6 下显示两行三列的六个“目标/值”槽，六个特效值彼此独立。6.1–6.5 仍使用原来的三角色、一兵种和共享特效值布局。旧地址 `0x00507800` 是另一张动态分组表，不再用于 6.6 天赋读写。

### 环境与运行

推荐 32 位 Python 3.8-3.11。目标游戏和发布用 Python 都必须是 32 位。

```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

本机开发和 UI 测试使用已有 Conda 环境：

```powershell
conda activate banshou
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

`banshou` 为 64 位时，证据采集器会通过 WOW64 API 读取 32 位目标线程上下文；正式发布仍优先使用 32 位解释器。

推荐的 Release 打包方式：

```powershell
conda activate banshou32
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

`banshou32` 必须是 32 位 Python 3.8-3.11。脚本会安装锁定的开发/Release 依赖、拒绝 64 位解释器、运行语法编译和单元测试，然后使用 `banshou66.spec` 生成 `dist\6.6扳手.exe` 和对应 `.sha256`。spec 会从当前 Conda 环境的 `Library\bin` 显式收集 `_ctypes/_lzma/_bz2` 所需的 `ffi.dll/liblzma.dll/libbz2.dll`，避免 PyInstaller 5.13 漏收 Conda 运行库。构建完成后脚本会启动产物并拒绝任何 `Unhandled exception` 或 `Failed to execute script` 窗口。构建临时文件、pip 缓存和 PyInstaller 缓存默认写入源码目录的 `build-temp`，不依赖系统盘剩余空间；需要改到其它磁盘时先设置 `$env:BANSHOU_BUILD_TEMP='F:\banshou-build-temp'`。原 `build_32bit.bat` 继续保留为兼容入口，但新脚本和 spec 不依赖 CMD 中文代码页。`DIY.csv` 仍是可选用户文件；源码没有提供默认内容，因此不会自动生成。

PyInstaller 5.13 仍依赖 `pkg_resources`，因此 `requirements.txt` 将 setuptools 限制为 `<81`。常规开发环境由 `requirements-dev.txt` 使用 Capstone 5.0.3；32 位 Windows 没有该版本的预编译 wheel，`requirements-dev-32.txt` 因此固定使用 API 兼容的 Capstone 4.0.2。正式扳手不打包仅供开发使用的 Capstone。

### 安全边界

- 进程以查询、读、写和内存操作的最小常用权限附加；仅远程调用期间临时申请创建线程权限。
- 1/2/4 字节读写使用独立的零初始化宽度，所有写入检查范围、API 字节数和写后复读。
- 代码补丁先匹配原字节或本工具补丁字节，多站点失败会回滚；关闭时只恢复本工具实际取得所有权的补丁。
- 动态 stub 先以 RW 页写入和复读，再切换为 RX 并刷新指令缓存；释放前暂停目标线程并确认没有 EIP 落在 stub 内。外部改码时不恢复调用点、不释放可能仍被引用的 stub。
- 证据 JSON 同时校验内容摘要、原始样本摘要和目录清单摘要；两个指定基底必须提供同一配方，通用采集结果不能靠人工布尔值升级。
- 进程重新附加、退出和窗口关闭时释放句柄；锁血、锁蓝和自动复活由 UI 线程的 1 秒 `QTimer` 执行。
- 兼容读写失败会把具体地址、宽度和错误显示到原状态标签，不再静默表现为全零数据。
- “不分敌我”使用 6.6 的四个完整分支站点，转向使用 `0x4575B8` 的六参数 ABI；不再写 `0x4242B0` 或调用旧 `0x457428`。
- 自动回归复用 `0x421175` 原生二次行动特技，并事务 NOP `0x412D82/0x43D529/0x43D540` 三个限制分支；不修改旧 A/B CALL，也不会写旧代码洞 `0x485E00`。6.6 布尔变量使用 `0x492FC8..0x4931C7` 的 512 字节 MSB-first bitset；装备限制为 ID `0..159`，标准消耗品固定为 ID `160..199`，数量地址由四组签名共同定位为 `BYTE[0x493AF0+ID-160]`，不会强写 `0x4B09DB` 或 `0x510C80`。
- 战场保存不调用旧 UI 从未使用的坐标和天气 helper；方向变化仍按原按钮行为即时刷新。

### 外部依据

- 原作者源码：https://github.com/Puluomiyuhun/Modifier-for-CaoCaoZhuan
- 6.3/6.4 系统笔记：https://xycq.org.cn/forum/thread-309777-1-1.html
- 6.5 发布帖：https://xycq.org.cn/forum/thread-309778-1-1.html
- 6.6 修正版发布帖：https://www.xycq.org.cn/forum/thread-310256-1-1.html

考虑到曹操传基本只有国人玩，所以readme文档我就用中文写了。<br>
这是一个曹操传的通用调试器的源码，里面实现了游戏的各种修改项，包括逻辑控制、角色属性、战场信息、仓库道具、人物天赋、必杀分配、变量修改、自定义修改项等功能。<br>
发布帖请见：http://www.xycq.online/forum/viewthread.php?tid=310288&extra=page%3D1<br>
修改器全部由python完成，界面由pyQt5完成，简单介绍下各个文件的功用：<br>
untitled.ui：这个文件是ui界面的文件，可以有qt designer打开，可以通过"pyuic5 -o untitled.py untitled.ui"指令将ui文件编译为python格式；<br>
main.py：这个文件是外挂的入口，主要用来呼出窗体；<br>
mywindow.py：这个文件是外挂的核心程序，里面包含了窗体的构造、用户输入消息和槽以及外挂的核心功能实现；<br>
hook.py：这个文件是用来做线程注入的，原理是将要执行的代码和栈信息注入到游戏本体，再创建一个新线程去执行该代码。<br>
<br>
版本信息：<br>
2022.5.21<br>
1、复刻旧扳手全部功能<br>
<br>
2022.5.23<br>
1、将天赋做成独立页面，加入专属、套装修改功能<br>
2、加入变量监控页面<br>
3、加入自定义修改页面<br>
<br>
2022.6.3<br>
1、加入必杀修改页面<br>
<br>
2022.6.26<br>
1、修复6.2自动回归闪退的bug<br>
<br>
2022.7.1<br>
1、合并6.3mp+和6.3，扳手自行判断是否扩展过mp上限<br>
<br>
v0.11   2022.7.3<br>
1、修复“一键全宝”会得到普通装备的bug<br>
2、设定“一键全宝”可以根据等级、经验输入框的数值，统一所有获得宝物的等级、经验<br>
3、修复“清空仓库”不能清零道具的bug<br>
<br>
v0.12   2022.7.4<br>
1、修复“人物”页面只要点保存就会变成我军的bug<br>
<br>
v0.13   2022.7.13<br>
1、修复变量范围错误的bug<br>
2、开放变量保存功能<br>
<br>
v0.14   2022.8.16<br>
1、修复天气显示、修改错误的bug<br>
<br>
v0.15   2022.9.10<br>
1、托管时可控友军可一并托管<br>
2、R场景手动单挑时只保存hp、mp，避免R剧情无限循环<br>
3、修正了扳手buff一回合就掉的问题<br>
4、新增功能：自动复活<br>
5、“全灭敌军”更改为“全灭范围内敌军”，可手动设置全灭范围<br>
6、新增扳手智能判断版本功能<br>
<br>
v0.16  2023.4.7<br>
1、不良状态扩展的适配<br>
<br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_6f772e487acc4f7d1e04Bd9liJiml8Ny.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_082a5692646123490ea8alJAfMCcYAn4.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_71318ea037f7b5979ac3k3UykS7X0hpa.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_253b26a22083acc82497sYeBud1lQygA.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_e384f269358e65ed1a94Zvin44nZOlRp.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_7057966f420d4903ce19etfXCM8ASVBI.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_b6cb750d1b0c320b7c8aYFIj0rJpUYwR.png" width = "500"><br>
<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_6de0e07619753bdd2f3asRAg4sB86hIl.png" width = "500"><br>

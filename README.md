# Modifier-for-CaoCaoZhuan

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

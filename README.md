# Modifier-for-CaoCaoZhuan

考虑到曹操传基本只有国人玩，所以readme文档我就用中文写了。<br>
这是一个曹操传的通用调试器的源码，里面实现了游戏的各种修改项，包括逻辑控制、角色属性、战场信息、仓库道具、人物天赋、必杀分配、变量修改、自定义修改项等功能。<br>
修改器全部由python完成，界面由pyQt5完成，简单介绍下各个文件的功用：<br>
untitled.ui：这个文件是ui界面的文件，可以有qt designer打开，可以通过"pyuic5 -o untitled.py untitled.ui"指令将ui文件编译为python格式；
main.py：这个文件是外挂的入口，主要用来呼出窗体；
mywindow.py：这个文件是外挂的核心程序，里面包含了窗体的构造、用户输入消息和槽以及外挂的核心功能实现；
hook.py：这个文件是用来做线程注入的，原理是将要执行的代码和栈信息注入到游戏本体，再创建一个新线程去执行该代码。

<img src="http://www.xycq.online/forum/attachments/forumid_76/20220701_71318ea037f7b5979ac3k3UykS7X0hpa.png" width = "500">

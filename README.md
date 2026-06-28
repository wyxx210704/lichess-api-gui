# lichess-api-gui，版本1.4
- 本项目为wyxx210704原创项目，继承此项目请遵循MIT协议
- 主要功能：为lichess api添加一个图形界面，方便控制

# 使用教程
## 一、为自己的账号添加API访问令牌（token）
1. 先进入[此页面](https://lichess.org/account/oauth/token)，点右上角+按钮，然后就会进入以下页面
![image.png](https://api.keepwork.com/ts-storage/siteFiles/49798/raw#1782219326915image.png)
2. 先填好令牌（token）描述，只要能让自己记住就行
3. 按需要勾选令牌（token）可执行的功能
4. 滑到底部，点右下角创建按钮，即可创建

## 二、运行程序
### python要求
- **绝对不能**是python**3.14**，不然运行时候一登录，json就起冲突
- 建议**python3.13**，不仅能保持最新，而且又不会出现依赖冲突
- 必须有这两个库
    - PyQt6
    - berserk
- 满足了以上要求即可运行
### 运行方式
windows双击该项目跟目录的`run.bat`即可运行
macos/linux双击该项目根目录的`run.sh`即可运行

macos/linux用户在运行前需要**额外添加执行权限**
`chmod +x run.sh`
### 运行结果
在运行过程中，每一个向API发送请求的操作都要等待两三秒，这两三秒内，**请不要动窗口**，不然就会搞未响应

首先会弹出一个登录窗口，然后就把前文提到的token输入进去，再点下面登录按钮就能登录
登录成功时会自动跳转到主窗口，登录失败就会放出报错的原因并且不会跳转，保留在这个对话框
![image.png](https://api.keepwork.com/ts-storage/siteFiles/49799/raw#1782222527843image.png)
然后会跳转到主页面
![image.png](https://api.keepwork.com/ts-storage/siteFiles/49800/raw#1782222745893image.png)

- 菜单栏中是已经更新好的各个API请求
- 请求返回的内容都会显示在下面这个树形组件里面
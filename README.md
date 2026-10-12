<h1>lichess-api</h1>
<a href="https://wyxx210704.github.io/lichess-api-gui/" target="_blank">点这里查看完整文档</a>

<h1>项目介绍</h1>
<ul>
    <li>本项目为wyxx210704原创项目，继承此项目请遵循MIT协议</li>
    <li>主要功能：为lichess api添加一个图形界面，方便控制</li>
</ul>
<a href="https://github.com/wyxx210704/lichess-api-gui" target="_blank">跳转到原项目</a>

<h1>使用教程</h1>

<h2>二、运行程序</h2>
<h3>python要求</h3>
<ul>
    <li><b>绝对不能</b>是python<b>3.14</b>，不然运行时候一登录，json就起冲突</li>
    <li>建议<b>python3.13</b>，不仅能保持最新，而且又不会出现依赖冲突</li>
    <li>
        必须有这几个库
        <br>
        <ul>
            <li>PyQt6</li>
            <li>python-chess</li>
            <li>berserk</li>
            <li>pyqt6-webengine</li>
        </ul>
    </li>
    <li>满足以上要求即可运行</li>
</ul>

<h3>运行方式</h3>
<p>
    main.py从主程序运行
    start_play_chess.py直接从下棋页面运行
</p>

<h3>运行结果</h3>
<p>
    在运行过程中，每一个向API发送请求的操作都要等待两三秒，这两三秒内，<b>请不要动窗口</b>，不然就会搞未响应<br>
    <br>
    首先会弹出一个登录窗口，然后按 步鄹进行登录<br>
    登录成功时会自动跳转到主窗口，登录失败就会放出报错的原因并且不会跳转，保留在这个对话框<br>
</p>